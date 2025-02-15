import { useState, useEffect } from "react";
import { fetchTradeSignals } from "../api";

const TradeSignals = () => {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    fetchTradeSignals().then(data => setSignals(data));
  }, []);

  return (
    <div className="p-4 bg-gray-800 text-white rounded-lg">
      <h2 className="text-lg font-bold">📊 Trade Signals</h2>
      <ul>
        {signals.map((signal, index) => (
          <li key={index} className="border-b p-2">
            {signal.timestamp} - <span className="font-bold">{signal.signal}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TradeSignals;
