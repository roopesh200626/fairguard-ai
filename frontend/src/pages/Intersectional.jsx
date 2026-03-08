import { useState } from 'react';
import { runIntersectional } from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { GitMerge, AlertCircle } from 'lucide-react';

export default function Intersectional() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [attrs] = useState(['Gender', 'Age', 'Location', 'Income']);
  const [selectedAttrs, setSelectedAttrs] = useState(['Gender', 'Location']);
  
  const handleToggle = (attr) => {
    if (selectedAttrs.includes(attr)) {
      if (selectedAttrs.length > 2) {
        setSelectedAttrs(selectedAttrs.filter(a => a !== attr));
      } else {
        alert("Select at least 2 attributes");
      }
    } else {
      setSelectedAttrs([...selectedAttrs, attr]);
    }
  };

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      const data = await runIntersectional(selectedAttrs);
      setResults(data.results);
    } catch (err) {
      alert("Error running intersectional analysis: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Sort results by Approval Rate
  const chartData = results 
    ? [...results].sort((a, b) => a['Approval Rate'] - b['Approval Rate']).map(r => ({ ...r, PPR_Pct: r['Approval Rate'] * 100 }))
    : [];

  const worstGroup = chartData.length > 0 ? chartData[0] : null;
  const bestGroup = chartData.length > 0 ? chartData[chartData.length - 1] : null;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="glass-header flex justify-between items-center">
        <div>
          <h2 className="text-xl">Intersectional Bias Analysis</h2>
          <p className="text-sm text-gray-400">Detect compounded bias across intersecting demographic groups.</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-heading mb-4">Select Attributes to Intersect</h3>
        <div className="flex flex-wrap gap-3 mb-6">
          {attrs.map(attr => (
            <button
              key={attr}
              onClick={() => handleToggle(attr)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                selectedAttrs.includes(attr) 
                  ? 'bg-secondary text-white border-2 border-secondary' 
                  : 'bg-surface border-2 border-border text-gray-400 hover:border-gray-500'
              }`}
            >
              {attr}
            </button>
          ))}
        </div>
        <button 
          onClick={handleAnalyze}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-secondary to-primary hover:from-purple-400 hover:to-cyan-400 text-background font-bold px-6 py-2 rounded-lg transition-transform hover:scale-105"
        >
          {loading ? <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin"></div> : <GitMerge size={20} />}
          {loading ? 'Computing Intersections...' : 'Analyze Intersectional Bias'}
        </button>
      </div>

      {!results && !loading && (
        <div className="card text-center py-16 text-gray-400">
          <AlertCircle size={48} className="mx-auto mb-4 opacity-50" />
          <p>Select attributes and click Analyze to uncover intersectional bias.</p>
        </div>
      )}

      {results && (
        <div className="animate-slide-up">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="card border-l-4 border-red-500 bg-red-900/10">
              <h3 className="text-red-400 font-heading mb-2 uppercase tracking-wider text-xs font-bold">Most Disadvantaged Group</h3>
              <div className="text-2xl font-bold text-white leading-tight mb-2">
                {worstGroup?.Group || "N/A"}
              </div>
              <div className="text-4xl font-bold text-red-500 mt-4">
                {worstGroup ? worstGroup.PPR_Pct.toFixed(1) : "0.0"}% <span className="text-sm text-red-400/70 font-normal">Approval Rate</span>
              </div>
            </div>
            
            <div className="card border-l-4 border-emerald-500 bg-emerald-900/10">
              <h3 className="text-emerald-400 font-heading mb-2 uppercase tracking-wider text-xs font-bold">Most Favored Group</h3>
              <div className="text-2xl font-bold text-white leading-tight mb-2">
                {bestGroup?.Group || "N/A"}
              </div>
              <div className="text-4xl font-bold text-emerald-500 mt-4">
                {bestGroup ? bestGroup.PPR_Pct.toFixed(1) : "0.0"}% <span className="text-sm text-emerald-400/70 font-normal">Approval Rate</span>
              </div>
            </div>
          </div>

          <div className="card h-[500px] flex flex-col">
            <h3 className="font-heading mb-4 text-white">Intersectional Group Disparity (Approval Rate)</h3>
            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 140, right: 20, top: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#252B42" horizontal={true} vertical={false} />
                  <XAxis type="number" tick={{ fill: '#888' }} domain={[0, 100]} />
                  <YAxis type="category" dataKey="Group" tick={{ fill: '#bbb', fontSize: 11 }} width={110} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e2130', borderColor: '#252B42', color: '#fff' }} />
                  <Bar dataKey="PPR_Pct" fill="#00e5ff" radius={[0, 4, 4, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card mt-6 overflow-x-auto">
            <h3 className="font-heading mb-4 text-white">Full Results Table</h3>
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="bg-surface text-gray-400 font-medium border-b border-border">
                <tr>
                  <th className="px-4 py-3">Group Identity</th>
                  <th className="px-4 py-3 text-right">Sample Size (n)</th>
                  <th className="px-4 py-3 text-right">Approval Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {chartData.map((row, i) => (
                  <tr key={i} className="hover:bg-surface/50">
                    <td className="px-4 py-3 text-gray-300 font-medium">{row.Group}</td>
                    <td className="px-4 py-3 text-gray-400 text-right">{row.Count}</td>
                    <td className="px-4 py-3 text-primary font-bold text-right">{row.PPR_Pct.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
