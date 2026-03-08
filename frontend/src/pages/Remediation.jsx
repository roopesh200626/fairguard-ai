import { useState } from 'react';
import { runDebias } from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { Wrench, CheckCircle } from 'lucide-react';

export default function Remediation() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [best, setBest] = useState(null);
  const [sensitiveAttr, setSensitiveAttr] = useState('Gender');

  const handleFixBias = async () => {
    try {
      setLoading(true);
      const data = await runDebias(sensitiveAttr);
      setResults(data.results);
      setBest(data.best);
    } catch (err) {
      alert("Error running debiasing: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = results?.map(r => ({
    name: r.method,
    Bias: r.dp_diff,
    Accuracy: r.accuracy * 100
  })) || [];

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="glass-header flex justify-between items-center">
        <div>
          <h2 className="text-xl">Bias Remediation Engine</h2>
          <p className="text-sm text-gray-400">Apply mitigation algorithms to fix bias while preserving accuracy.</p>
        </div>
      </div>

      <div className="card border-primary/20">
        <div className="flex flex-col md:flex-row md:items-end gap-6 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-400 mb-2">Primary Target Attribute for Remediation</label>
            <select 
              value={sensitiveAttr}
              onChange={(e) => setSensitiveAttr(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary"
            >
              <option value="Gender">Gender</option>
              <option value="Age">Age</option>
              <option value="Location">Location</option>
            </select>
          </div>
          <button 
            onClick={handleFixBias}
            disabled={loading}
            className="flex items-center justify-center gap-2 bg-primary hover:bg-cyan-400 text-background font-bold px-8 py-3 rounded-xl transition-all shadow-lg shadow-primary/20"
          >
            {loading ? <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin"></div> : <Wrench size={20} />}
            {loading ? 'Applying Mitigation...' : 'Fix Bias'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card bg-surface2/50 border-l-4 border-gray-500">
          <h4 className="font-heading mb-1 text-white">1. Reweighing</h4>
          <p className="text-xs text-gray-400">Pre-processing technique that assigns weights to training examples so groups have equal representation.</p>
        </div>
        <div className="card bg-surface2/50 border-l-4 border-gray-500">
          <h4 className="font-heading mb-1 text-white">2. Threshold Optimization</h4>
          <p className="text-xs text-gray-400">Post-processing technique that finds group-specific thresholds to equalize positive outcome rates.</p>
        </div>
        <div className="card bg-surface2/50 border-l-4 border-gray-500">
          <h4 className="font-heading mb-1 text-white">3. Adversarial Debiasing</h4>
          <p className="text-xs text-gray-400">In-processing technique that jointly trains a predictor and an adversary predicting the protected attribute.</p>
        </div>
      </div>

      {loading && (
        <div className="card py-16 text-center animate-pulse">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h3 className="text-xl font-heading text-white">Training Debiased Models...</h3>
          <p className="text-gray-400">This may take a moment. Evaluating Original, Reweighing, Threshold Optimization, and Adversarial approaches.</p>
        </div>
      )}

      {results && best && (
        <div className="animate-slide-up">
          <div className="bg-gradient-to-r from-emerald-900/40 to-primary/10 border border-emerald-500/30 rounded-xl p-6 mb-8 text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
            <CheckCircle className="mx-auto text-emerald-400 mb-3" size={48} />
            <h3 className="text-2xl font-bold text-white mb-2">Remediation Successful</h3>
            <p className="text-lg text-gray-300">
              Best Method: <span className="text-emerald-400 font-bold">{best.method}</span>
            </p>
            <p className="text-gray-400 mt-2">
              Bias Score reduced to <span className="font-bold text-white">{best.dp_diff.toFixed(3)}</span> 
              &nbsp;(Original: {results[0].dp_diff.toFixed(3)})
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card min-h-[400px] flex flex-col">
              <h3 className="font-heading mb-4 text-white">Bias Before & After (Lower is Better)</h3>
              <div className="flex-1 min-h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252B42" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#888', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#888' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e2130', borderColor: '#252B42', color: '#fff' }} />
                    <Bar dataKey="Bias" fill="#e74c3c">
                      {chartData.map((entry, index) => (
                        <cell key={`cell-${index}`} fill={index === 0 ? '#e74c3c' : index === chartData.findIndex(d => d.name === best.method) ? '#2ecc71' : '#f39c12'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card min-h-[400px] flex flex-col">
              <h3 className="font-heading mb-4 text-white">Accuracy Preserved (Higher is Better)</h3>
              <div className="flex-1 min-h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252B42" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#888', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#888' }} domain={['dataMin - 5', 'dataMax + 5']} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e2130', borderColor: '#252B42', color: '#fff' }} />
                    <Bar dataKey="Accuracy" fill="#3498db" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
          <div className="card mt-6">
            <h3 className="font-heading mb-4 text-white">Comparison Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="bg-surface text-gray-400 font-medium border-b border-border">
                  <tr>
                    <th className="px-4 py-3">Method</th>
                    <th className="px-4 py-3 text-right">Accuracy</th>
                    <th className="px-4 py-3 text-right">Bias (DP Diff)</th>
                    <th className="px-4 py-3 text-right">Bias Reduction</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {results.map((r, i) => {
                    const origDp = results[0].dp_diff;
                    const isBest = r.method === best.method;
                    const reduction = Math.max(0, ((origDp - r.dp_diff) / origDp) * 100);
                    
                    return (
                      <tr key={i} className={`hover:bg-surface/50 ${isBest ? 'bg-emerald-900/10' : ''}`}>
                        <td className="px-4 py-3 font-medium flex items-center gap-2">
                          <span className={isBest ? 'text-emerald-400' : 'text-gray-300'}>{r.method}</span>
                          {isBest && <span className="bg-emerald-500/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider">Best</span>}
                        </td>
                        <td className="px-4 py-3 text-right text-gray-300">{(r.accuracy * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-right font-mono" style={{ color: r.dp_diff < 0.1 ? '#2ecc71' : '#f39c12' }}>
                          {r.dp_diff.toFixed(3)}
                        </td>
                        <td className="px-4 py-3 text-right text-primary font-bold">
                          {i === 0 ? '—' : `${reduction.toFixed(0)}%`}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
