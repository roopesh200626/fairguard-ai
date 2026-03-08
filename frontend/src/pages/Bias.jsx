import { useState } from 'react';
import { runAudit } from '../api';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { PlayCircle, AlertTriangle } from 'lucide-react';

export default function Bias() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [attrs, setAttrs] = useState(['Gender', 'Age', 'Location', 'Income']);

  const handleAudit = async () => {
    try {
      setLoading(true);
      const data = await runAudit(attrs);
      setResults(data.audit_results);
    } catch (err) {
      alert("Error running audit: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const classifySeverity = (score) => {
    if (score < 0.10) return { label: 'Low', class: 'badge-low', color: '#2ecc71' };
    if (score < 0.15) return { label: 'Moderate', class: 'badge-moderate', color: '#f39c12' };
    if (score < 0.20) return { label: 'High', class: 'badge-high', color: '#e74c3c' };
    return { label: 'Critical', class: 'badge-critical', color: '#ff4444' };
  };

  // Format data for Radar Chart
  const getRadarData = () => {
    if (!results) return [];
    return Object.keys(results).map(attr => ({
      attribute: attr,
      score: results[attr].demographic_parity_diff
    }));
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="glass-header flex justify-between items-center">
        <div>
          <h2 className="text-xl">Bias Analysis</h2>
          <p className="text-sm text-gray-400">Detect bias across protected attributes using standard fairness metrics.</p>
        </div>
        <button 
          onClick={handleAudit}
          disabled={loading}
          className="flex items-center gap-2 bg-primary hover:bg-cyan-400 text-background font-bold px-6 py-2 rounded-lg transition-colors"
        >
          {loading ? <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin"></div> : <PlayCircle size={20} />}
          {loading ? 'Running Audit...' : 'Run Bias Audit'}
        </button>
      </div>

      {!results && !loading && (
        <div className="card text-center py-16 text-gray-400">
          <AlertTriangle size={48} className="mx-auto mb-4 opacity-50" />
          <p>Click "Run Bias Audit" to analyze the loaded model.</p>
        </div>
      )}

      {loading && (
        <div className="card text-center py-16 flex flex-col items-center justify-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <h3 className="text-xl font-heading text-white mb-2 animate-pulse">Running Full Fairness Audit</h3>
          <p className="text-sm text-gray-400">Computing Demographic Parity, Equal Opportunity, and Predictive Parity...</p>
        </div>
      )}

      {results && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-slide-up">
            {Object.keys(results).map(attr => {
              const res = results[attr];
              const sev = classifySeverity(res.demographic_parity_diff);
              return (
                <div key={attr} className="metric-card">
                  <div className="flex justify-between items-start mb-2">
                    <h3>{attr} Bias</h3>
                    <span className={sev.class}>{sev.label}</span>
                  </div>
                  <div className="val" style={{ color: sev.color }}>
                    {res.demographic_parity_diff.toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 uppercase tracking-wide">Demographic Parity Diff</div>
                </div>
              );
            })}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="card md:col-span-1 min-h-[300px] flex flex-col">
              <h3 className="font-heading mb-4 text-white">Bias Radar (DP Diff)</h3>
              <div className="flex-1 min-h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={getRadarData()}>
                    <PolarGrid stroke="#252B42" />
                    <PolarAngleAxis dataKey="attribute" tick={{ fill: '#888', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 'auto']} tick={{ fill: '#555' }} />
                    <Radar name="Bias Score" dataKey="score" stroke="#00e5ff" fill="#00e5ff" fillOpacity={0.4} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e2130', borderColor: '#252B42', color: '#fff' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card md:col-span-2 min-h-[300px] flex flex-col">
              <h3 className="font-heading mb-4 text-white">Approval Rates by Group</h3>
              <div className="flex-1 min-h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={
                    // Flatten approval rates for all attributes
                    Object.keys(results).reduce((acc, attr) => {
                      const stats = results[attr].group_stats;
                      Object.keys(stats).forEach(group => {
                        acc.push({ name: `${attr}: ${group}`, Rate: stats[group].ppr * 100 });
                      });
                      return acc;
                    }, [])
                  }>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252B42" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#888', fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                    <YAxis tick={{ fill: '#888' }} domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e2130', borderColor: '#252B42', color: '#fff' }} />
                    <Bar dataKey="Rate" fill="#7b61ff" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
          <div className="space-y-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            {Object.keys(results).map(attr => (
              <div key={attr} className="card bg-surface2/50">
                <h4 className="border-b border-border pb-2 mb-4 font-heading text-lg text-primary">{attr} Detailed Metrics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div>
                    <div className="text-xs text-gray-500 uppercase">Demographic Parity</div>
                    <div className="text-lg font-bold text-white">{results[attr].demographic_parity_diff.toFixed(3)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase">Equal Opportunity</div>
                    <div className="text-lg font-bold text-white">{results[attr].equal_opportunity_diff.toFixed(3)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase">Predictive Parity</div>
                    <div className="text-lg font-bold text-white">{results[attr].predictive_parity_diff.toFixed(3)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase">Disparate Impact</div>
                    <div className="text-lg font-bold text-white">{results[attr].disparate_impact_ratio.toFixed(3)}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
