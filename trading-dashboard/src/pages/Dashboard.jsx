import TradeSignals from "../components/TradeSignals";
import SentimentChart from "../components/SentimentChart";
import PerformanceMetrics from "../components/PerformanceMetrics";

const Dashboard = () => {
  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      <TradeSignals />
      <SentimentChart />
      <PerformanceMetrics />
    </div>
  );
};

export default Dashboard;
