import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load API keys (No API key required for The Graph, but store URLs in .env)
load_dotenv()
GRAPH_API_URL_UNISWAP = os.getenv("GRAPH_API_URL_UNISWAP", "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
GRAPH_API_URL_AAVE = os.getenv("GRAPH_API_URL_AAVE", "https://api.thegraph.com/subgraphs/name/aave/protocol-v2")

# Function to fetch Uniswap trading volume & liquidity
def fetch_uniswap_data():
    query = """
    {
      pools(first: 5, orderBy: volumeUSD, orderDirection: desc) {
        id
        volumeUSD
        totalValueLockedUSD
        token0 { symbol }
        token1 { symbol }
      }
    }
    """
    response = requests.post(GRAPH_API_URL_UNISWAP, json={"query": query}).json()
    
    if "errors" in response:
        print(f"❌ GraphQL Error (Uniswap): {response['errors'][0]['message']}")
        return

    pools = response.get("data", {}).get("pools", [])

    if pools:
        df = pd.DataFrame(pools)
        df.to_csv("data/onchain_uniswap_data.csv", index=False)
        print("✅ Uniswap data saved to data/onchain_uniswap_data.csv")
    else:
        print("⚠️ No Uniswap data found!")

# Function to fetch Aave token, reward token, and totalLiquidity data
def fetch_aave_data():
    query = """
    {
      tokens(first: 5) {
        id
        name
        symbol
        decimals
      }
      rewardTokens(first: 5) {
        id
        token { id }
        type
        _distributionEnd
      }
      # reserves(first: 5, orderBy: totalLiquidity, orderDirection: desc) {
      #   id
      #   symbol
      #   totalLiquidity
      # }
    }
    """
    response = requests.post(GRAPH_API_URL_AAVE, json={"query": query}).json()

    if "errors" in response:
        print(f"❌ GraphQL Error (Aave): {response['errors'][0]['message']}")
        return

    # Extract data from API response
    tokens = response.get("data", {}).get("tokens", [])
    reward_tokens = response.get("data", {}).get("rewardTokens", [])
    reserves = response.get("data", {}).get("reserves", [])

    # Save token data
    if tokens:
        df_tokens = pd.DataFrame(tokens)
        df_tokens.to_csv("data/onchain_aave_tokens.csv", index=False)
        print("✅ Aave token data saved to data/onchain_aave_tokens.csv")
    else:
        print("⚠️ No Aave tokens found!")

    # Save reward token data
    if reward_tokens:
        df_rewards = pd.DataFrame(reward_tokens)
        df_rewards.to_csv("data/onchain_aave_rewards.csv", index=False)
        print("✅ Aave reward token data saved to data/onchain_aave_rewards.csv")
    else:
        print("⚠️ No Aave reward tokens found!")

    # Save reserves (liquidity data)
    if reserves:
        df_reserves = pd.DataFrame(reserves)
        df_reserves.to_csv("data/onchain_aave_liquidity.csv", index=False)
        print("✅ Aave liquidity data saved to data/onchain_aave_liquidity.csv")
    else:
        print("⚠️ No Aave liquidity data found!")

if __name__ == "__main__":
    fetch_uniswap_data()
    fetch_aave_data()
