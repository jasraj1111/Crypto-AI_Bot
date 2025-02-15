const API_BASE_URL = "http://localhost:5000/api"; // Flask Backend

export const fetchTradeSignals = async () => {
  const res = await fetch(`${API_BASE_URL}/trade-signals`);
  return res.json();
};

export const fetchBacktestResults = async () => {
  const res = await fetch(`${API_BASE_URL}/backtest-results`);
  return res.json();
};
