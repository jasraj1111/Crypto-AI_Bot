import { useState, useEffect } from "react";
import { fetchBacktestResults } from "../api";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const SentimentChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchBacktestResults().then(results => {
      // Filter only trade-related rows
      const tradeData = results.filter(row => row.metric_name === "Trade").map((row, index) => ({
        time: new Date(row.timestamp).toLocaleString(),
        price: parseFloat(row.price),
        action: row.action
      }));
      setData(tradeData);
    });
  }, []);

  return (
    <div className="p-4 bg-gray-800 text-white rounded-lg">
      <h2 className="text-lg font-bold">📈 Trade Execution Trend</h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <XAxis dataKey="time" tick={{ fill: "#fff", fontSize: 12 }} />
          <YAxis tick={{ fill: "#fff", fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#82ca9d" dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SentimentChart;
