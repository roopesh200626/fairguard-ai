import { useState, useEffect } from 'react';
import { getCompliance, getCertificateUrl } from '../api';
import { Award, AlertTriangle, ShieldCheck, Download, Lock } from 'lucide-react';

export default function Certificate() {
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
        <h3 className="text-xl font-heading text-white">Verifying Certification Requirements</h3>
      </div>
    );
  }

  if (error) {
    return (
       <div className="card text-center py-24 text-gray-400 animate-fade-in">
        <AlertTriangle size={48} className="mx-auto mb-4 opacity-50" />
        <p>Run Bias Analysis first.</p>
        <p className="text-xs text-red-400 mt-2">{error}</p>
      </div>
    );
  }

  const { status, effective_dp, effective_acc } = data;
  const passed = effective_dp < 0.10;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div className="glass-header">
        <h2 className="text-xl">AI Fairness Audit Certificate</h2>
        <p className="text-sm text-gray-400">Generate a secure cryptographic certificate for audited models.</p>
      </div>

      {passed ? (
        <div className="max-w-3xl mx-auto mt-8 animate-slide-up">
          <div className="relative bg-gradient-to-b from-surface2 to-surface border-2 border-emerald-500 rounded-2xl p-12 overflow-hidden shadow-2xl shadow-emerald-500/20 text-center">
            
            {/* Watermark patterns */}
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <ShieldCheck size={200} className="text-emerald-500" />
            </div>
            <div className="absolute -left-12 -bottom-12 w-64 h-64 bg-emerald-500/20 rounded-full blur-3xl"></div>
            <div className="absolute -right-12 -top-12 w-64 h-64 bg-primary/20 rounded-full blur-3xl"></div>

            <div className="relative z-10 flex flex-col items-center">
              <div className="w-24 h-24 bg-emerald-900/40 rounded-full flex items-center justify-center border-4 border-emerald-500 mb-6 shadow-[0_0_30px_rgba(46,204,113,0.3)]">
                <Award size={48} className="text-emerald-400" />
              </div>

              <h1 className="text-4xl font-heading font-black tracking-widest text-emerald-400 mb-2 uppercase drop-shadow-lg">
                Certified Fair
              </h1>
              
              <div className="h-px w-32 bg-gradient-to-r from-transparent via-emerald-500 to-transparent my-6"></div>

              <p className="text-gray-300 text-lg mb-8 max-w-lg leading-relaxed font-body">
                This AI model has successfully passed the rigorous FairGuard algorithmic bias audit, 
                demonstrating non-discrimination across protected demographic attributes.
              </p>

              <div className="grid grid-cols-2 gap-8 w-full max-w-lg bg-background/50 p-6 rounded-xl border border-white/5 backdrop-blur-sm shadow-inner mb-8">
                <div className="text-center">
                  <p className="text-xs text-emerald-400/80 uppercase font-bold tracking-widest mb-1">Final Bias Score</p>
                  <p className="text-3xl font-mono text-emerald-400 font-bold">{effective_dp.toFixed(4)}</p>
                  <p className="text-xs text-gray-500 mt-1">Threshold: 0.1000</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-emerald-400/80 uppercase font-bold tracking-widest mb-1">Model Accuracy</p>
                  <p className="text-3xl font-mono text-white font-bold">{(effective_acc * 100).toFixed(1)}%</p>
                  <p className="text-xs text-gray-500 mt-1">Status: Verified</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-gray-500 font-mono tracking-widest mb-8">
                <Lock size={12} className="text-emerald-500/50" />
                SECURE ISSUANCE: {new Date().toISOString().split('T')[0]} • UID: {Math.random().toString(36).substr(2, 9).toUpperCase()}
              </div>

              <a 
                href={getCertificateUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-10 py-4 rounded-xl font-bold uppercase tracking-wider flex items-center gap-3 transition-all hover:scale-105 shadow-[0_0_20px_rgba(46,204,113,0.4)]"
              >
                <Download size={20} /> Download Official Certificate
              </a>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-2xl mx-auto mt-8 card border-t-4 border-red-500 bg-red-900/10 text-center py-16 px-8 relative overflow-hidden animate-slide-up">
           <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
           
           <div className="w-20 h-20 bg-red-900/50 rounded-full flex items-center justify-center border-2 border-red-500/50 mx-auto mb-6">
             <ShieldAlert size={40} className="text-red-500" />
           </div>
           
           <h2 className="text-3xl font-heading font-bold text-red-500 mb-4">Certification Failed</h2>
           
           <p className="text-gray-300 text-lg mb-8 max-w-md mx-auto">
             The current bias score of <span className="font-bold font-mono text-red-400 bg-red-900/30 px-2 py-1 rounded">{effective_dp.toFixed(4)}</span> exceeds the allowable threshold of <span className="font-bold text-white">0.1000</span>.
           </p>

           <div className="bg-background/50 p-6 rounded-xl border border-red-500/20 mb-8 inline-block shadow-inner">
             <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Required Action</h4>
             <p className="text-gray-300">
               Apply debiasing techniques in the <b className="text-primary">Bias Remediation</b> engine to bring the score below the threshold before a certificate can be issued.
             </p>
           </div>
        </div>
      )}
    </div>
  );
}
