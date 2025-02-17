// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

contract TradingBot is Ownable {
    ISwapRouter public immutable swapRouter;
    address public immutable WETH;
    address public immutable USDC;

    constructor(
        address _swapRouter,
        address _weth,
        address _usdc,
        address _initialOwner // Add initialOwner parameter
    ) Ownable(_initialOwner) { // Pass initialOwner to Ownable constructor
        swapRouter = ISwapRouter(_swapRouter);
        WETH = _weth;
        USDC = _usdc;
    }

    function executeTrade(uint256 amountIn, bool isBuy) external onlyOwner {
        require(amountIn > 0, "Amount must be greater than zero");

        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
            tokenIn: isBuy ? USDC : WETH,
            tokenOut: isBuy ? WETH : USDC,
            fee: 3000, // 0.3% fee tier on Uniswap V3
            recipient: msg.sender,
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0,
            sqrtPriceLimitX96: 0
        });

        IERC20(params.tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(params.tokenIn).approve(address(swapRouter), amountIn);
        swapRouter.exactInputSingle(params);
    }
}