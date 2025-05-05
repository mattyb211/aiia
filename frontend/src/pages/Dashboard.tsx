import { useState, useMemo } from 'react';
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

// –––––– Types ––––––
interface Allocation {
  ticker: string;
  allocation: number; // percentage
  price: number;
}

interface HistoryPoint {
  date: string;
  value: number;
}

// –––––– Helpers ––––––
const COLORS = [
  '#3b82f6',
  '#10b981',
  '#facc15',
  '#f97316',
  '#ef4444',
  '#8b5cf6',
  '#14b8a6',
  '#ec4899',
];

export default function Dashboard() {
  const [budget, setBudget] = useState(10_000);
  const [horizon, setHorizon] = useState(5);
  const [risk, setRisk] = useState(5);
  const [fundType, setFundType] = useState<'stocks' | 'etf' | 'mutual'>('stocks');
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post('/recommend', {
        budget,
        horizon,
        risk,
        fund_type: fundType,
      });

      setAllocations(data.holdings ?? []);
      setHistory(data.history ?? []);

      if (!data.holdings || data.holdings.length === 0) {
        setError('No recommendations were returned for this selection.');
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // build chart.js datasets only when allocations / history change
  const pieData = useMemo(() => {
    return {
      labels: allocations.map(a => a.ticker),
      datasets: [
        {
          data: allocations.map(a => a.allocation),
          backgroundColor: allocations.map((_, i) => COLORS[i % COLORS.length]),
          borderWidth: 1,
        },
      ],
    };
  }, [allocations]);

  const lineData = useMemo(() => {
    return {
      labels: history.map(h => h.date),
      datasets: [
        {
          label: 'Portfolio value',
          data: history.map(h => h.value),
          borderColor: '#3b82f6',
          tension: 0.3,
        },
      ],
    };
  }, [history]);

  // –––––– UI ––––––
  return (
    <div className="min-h-screen bg-neutral-900 text-white flex flex-col items-center p-6 space-y-6">
      <h1 className="text-4xl font-extrabold text-center">Investment Advisor Dashboard</h1>

      {/* --- Controls panel --- */}
      <div className="card w-full max-w-3xl space-y-4 p-6 bg-neutral-800 rounded-2xl shadow-lg">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block font-medium">Budget ($)</label>
            <input
              type="number"
              className="input w-full"
              value={budget}
              onChange={e => setBudget(Number(e.target.value))}
            />
          </div>

          <div className="space-y-2">
            <label className="block font-medium">Time horizon (years)</label>
            <input
              type="number"
              className="input w-full"
              value={horizon}
              onChange={e => setHorizon(Number(e.target.value))}
            />
          </div>

          <div className="space-y-2 col-span-full md:col-span-2">
            <label className="block font-medium">Risk tolerance (1‒10): {risk}</label>
            <input
              type="range"
              min={1}
              max={10}
              value={risk}
              onChange={e => setRisk(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <label className="block font-medium">Fund type</label>
            <select
              className="input w-full"
              value={fundType}
              onChange={e => setFundType(e.target.value as any)}
            >
              <option value="stocks">Stocks</option>
              <option value="etf">ETF</option>
              <option value="mutual">Mutual funds</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              className="btn btn-primary w-full"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? 'Generating…' : 'Generate Portfolio'}
            </button>
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>

      {/* --- Charts --- */}
      {allocations.length > 0 && (
        <div className="w-full max-w-xl bg-neutral-800 rounded-2xl p-4 shadow-lg">
          <Pie data={pieData} />
        </div>
      )}

      {history.length > 0 && (
        <div className="w-full max-w-xl bg-neutral-800 rounded-2xl p-4 shadow-lg">
          <Line data={lineData} />
        </div>
      )}
    </div>
  );
}
