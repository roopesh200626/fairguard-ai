import { useState, useEffect } from 'react';
import { getCompliance, getReportPdfUrl } from '../api';
import { FileCheck, Download, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

export default function Compliance() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCompliance();
  }, []);

  const loadCompliance = async () => {
    try {
      setLoading(true);
      const result = await getCompliance();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card text-center py-24 flex flex-col items-center justify-center animate-fade-in">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
        <h3 className="text-xl font-heading text-white">Generating Compliance Report</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-24 text-gray-400 animate-fade-in">
        <AlertTriangle size={48} className="mx-auto mb-4 opacity-50" />
        <p>Run Bias Analysis first to generate the compliance report.</p>
        <p className="text-xs text-red-400 mt-2">{error}</p>
      </div>
    );
  }

  const { status, effective_dp, effective_di, original_max_dp, regulations } = data;
  const passCount = regulations.filter(r => r.pass).length;
  const progressPercent = (passCount / regulations.length) * 100;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="glass-header flex justify-between items-center">
        <div>
          <h2 className="text-xl">Regulatory Compliance Report</h2>
          <p className="text-sm text-gray-400">Map fairness metrics to global AI regulations and standards.</p>
        </div>
        <a 
          href={getReportPdfUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-surface2 hover:bg-surface border border-primary text-primary font-bold px-6 py-2 rounded-lg transition-colors"
        >
          <Download size={18} /> Download Full PDF
        </a>
      </div>

      <div className={`card border-l-4 ${status === 'debiased' ? 'border-emerald-500 bg-emerald-900/10' : 'border-amber-500 bg-amber-900/10'}`}>
        <div className="flex items-start gap-4">
          {status === 'debiased' ? <CheckCircle className="text-emerald-400 mt-1" size={24} /> : <AlertTriangle className="text-amber-400 mt-1" size={24} />}
          <div>
            <h3 className={`text-lg font-bold ${status === 'debiased' ? 'text-emerald-400' : 'text-amber-400'}`}>
              {status === 'debiased' ? 'Using Debiased Model Scores' : 'Showing Original Model Scores'}
            </h3>
            <p className="text-gray-300 mt-1">
              {status === 'debiased' 
                ? `Bias reduced from ${original_max_dp.toFixed(3)} → ${effective_dp.toFixed(3)}.`
                : `Go to Bias Remediation and fix bias for better compliance results.`}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex justify-between items-end mb-4">
          <h3 className="text-2xl font-heading text-white">Compliance Score</h3>
          <div className="text-3xl font-bold text-primary">
            {passCount} <span className="text-xl text-gray-500">/ {regulations.length}</span>
          </div>
        </div>
        
        <div className="w-full h-4 bg-surface rounded-full overflow-hidden mb-2">
          <div 
            className={`h-full ${passCount === regulations.length ? 'bg-emerald-500' : passCount >= 4 ? 'bg-amber-500' : 'bg-red-500'} transition-all duration-1000`} 
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-400 uppercase tracking-wide font-semibold">
          {passCount === regulations.length ? 'Fully Compliant' : passCount >= 4 ? 'Action Required' : 'High Risk - Non-Compliant'}
        </p>
      </div>

      {status === 'debiased' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="metric-card !bg-red-900/10 !border-red-500 text-center py-6">
            <h3 className="!text-red-400 text-sm uppercase mb-2">Before Fix</h3>
            <div className="val !text-white !text-4xl">{original_max_dp.toFixed(3)}</div>
            <div className="sub mt-2 text-gray-400">Bias Score (DP Diff)</div>
          </div>
          <div className="metric-card !bg-emerald-900/10 !border-emerald-500 text-center py-6">
            <h3 className="!text-emerald-400 text-sm uppercase mb-2">After Fix</h3>
            <div className="val !text-white !text-4xl">{effective_dp.toFixed(3)}</div>
            <div className="sub mt-2 text-gray-400">Bias Score (DP Diff)</div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {regulations.map((reg, i) => (
          <div key={i} className={`p-5 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-300 hover:-translate-y-1 ${
            reg.pass 
              ? 'bg-emerald-900/20 border-emerald-800/50 hover:border-emerald-500' 
              : 'bg-red-900/20 border-red-800/50 hover:border-red-500'
          }`}>
            <div className="flex items-start gap-4">
              <div className="mt-1">
                {reg.pass ? <CheckCircle className="text-emerald-400" size={24} /> : <ShieldAlert className="text-red-500" size={24} />}
              </div>
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h4 className={`font-bold text-lg ${reg.pass ? 'text-emerald-400' : 'text-red-400'}`}>
                    {reg.name}
                  </h4>
                  <span className="text-xs bg-surface2 px-2 py-1 rounded text-gray-400">{reg.thresh}</span>
                </div>
                <p className="text-sm text-gray-300">{reg.desc}</p>
              </div>
            </div>
            <div className={`px-4 py-2 rounded-lg font-bold text-sm tracking-widest ${reg.pass ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-500'} self-start md:self-auto`}>
              {reg.pass ? 'PASS' : 'RISK'}
            </div>
          </div>
        ))}
      </div>
      
      <div className="flex justify-center mt-8">
        <a 
          href={getReportPdfUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-surface2 hover:bg-surface border border-gray-600 text-gray-300 px-8 py-3 rounded-lg transition-colors font-semibold"
        >
          <FileCheck size={18} /> Download Compliance Evidence (PDF)
        </a>
      </div>
    </div>
  );
}
