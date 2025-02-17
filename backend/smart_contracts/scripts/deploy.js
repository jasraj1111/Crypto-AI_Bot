const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deploying contract with account: ${deployer.address}`);

  const TradingBot = await hre.ethers.getContractFactory("TradingBot");
  const bot = await TradingBot.deploy(
    "0xE592427A0AEce92De3Edee1F18E0157C05861564", // Uniswap V3 Router on Mumbai
    "0x9c3c9283d3e44854697cd22d3faa240cfb032889", // WETH on Mumbai
    "0xFEca406dA9727A25E71e732F9961F680059eF1F9"  // USDC on Mumbai
  );

  await bot.deployed();
  console.log(`✅ TradingBot deployed at: ${bot.address}`);
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
