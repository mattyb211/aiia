import { useState } from 'react';
import api from '../services/api';
import { Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
} from 'chart.js';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
);

type Allocation = {
  symbol: string;
  percent: number;
};

type HistoryPoint = {
  date: string;
  value: number;
};

export default function Dashboard() {
  const [budget, setBudget] = useState(10000);
  const [horizon, setHorizon] = useState(5);
  const [risk, setRisk] = useState(5);
  const [fundType, setFundType] = useState<'stocks' | 'etf' | 'mutual'>('stocks');
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const { data } = await api.post('/recommend', {
        budget,
        horizon,
        risk,
        fund_type: fundType,
      });

      setAllocations(data.allocations);
      setHistory(data.history);
    } finally {
      setLoading(false);
    }
  };

  const pieData = {
    labels: allocations.map(a => a.symbol),
    datasets: [
      {
        data: allocations.map(a => a.percent),
      },
    ],
  };

  const lineData = {
    labels: history.map(h => h.date),
    datasets: [
      {
        label: 'Portfolio value',
        data: history.map(h => h.value),
      },
    ],
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-semibold">Investment Advisor Dashboard</h1>

      {/* --- Controls --- */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="card space-y-2">
          <label className="block font-medium">Budget ($)</label>
          <input
            type="number"
            className="input"
            value={budget}
            onChange={e => setBudget(Number(e.target.value))}
          />

          <label className="block font-medium">Time horizon (years)</label>
          <input
            type="number"
            className="input"
            value={horizon}
            onChange={e => setHorizon(Number(e.target.value))}
          />

          <label className="block font-medium">Risk tolerance (1‒10)</label>
          <input
            type="range"
            min={1}
            max={10}
            value={risk}
            onChange={e => setRisk(Number(e.target.value))}
            className="w-full"
          />

          <label className="block font-medium">Fund type</label>
          <select
            className="input"
            value={fundType}
            onChange={e => setFundType(e.target.value as any)}
          >
            <option value="stocks">Stocks</option>
            <option value="etf">ETF</option>
            <option value="mutual">Mutual funds</option>
          </select>

          <button
            className="btn btn-primary w-full mt-4"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? 'Generating…' : 'Generate Portfolio'}
          </button>
        </div>

        {/* --- Pie chart --- */}
        {allocations.length > 0 && (
          <div className="card flex items-center justify-center">
            <Pie data={pieData} />
          </div>
        )}
      </div>

      {/* --- History line --- */}
      {history.length > 0 && (
        <div className="card">
          <Line data={lineData} />
        </div>
      )}
    </div>
  );
}
