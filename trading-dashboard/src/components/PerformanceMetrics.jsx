import { useState, useEffect } from "react";
import { fetchBacktestResults } from "../api";

const PerformanceMetrics = () => {
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    fetchBacktestResults().then(results => {
      const metricMap = {};
      results.forEach(row => {
        if (row.metric_name) {
          metricMap[row.metric_name] = row.value;
        }
      });

      setMetrics({
        initialBalance: metricMap["Initial Balance"] || "$0.00",
        finalBalance: metricMap["Final Balance"] || "$0.00",
        totalReturn: metricMap["Total Return"] || "0%",
        winRate: metricMap["Win Rate"] || "0%",
        maxDrawdown: metricMap["Max Drawdown"] || "0%",
        profitFactor: metricMap["Profit Factor"] || "0",
        totalTrades: metricMap["Total Trades"] || "0"
      });
    });
  }, []);

  return (
    <div className="p-4 bg-gray-800 text-white rounded-lg">
      <h2 className="text-lg font-bold">📊 Performance Metrics</h2>
      <p>💰 Initial Balance: {metrics.initialBalance}</p>
      <p>🏁 Final Balance: {metrics.finalBalance}</p>
      <p>📈 Total Return: {metrics.totalReturn}</p>
      <p>🏆 Win Rate: {metrics.winRate}</p>
      <p>📉 Max Drawdown: {metrics.maxDrawdown}</p>
      <p>💰 Profit Factor: {metrics.profitFactor}</p>
      <p>🔄 Total Trades: {metrics.totalTrades}</p>
    </div>
  );
};

export default PerformanceMetrics;
