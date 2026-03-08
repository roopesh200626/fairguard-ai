import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Rocket, Database, Settings } from 'lucide-react';
import { loadDemo, uploadFiles } from '../api';

export default function Setup() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [demoLoaded, setDemoLoaded] = useState(false);
  const [preview, setPreview] = useState(null);
  
  const [modelFile, setModelFile] = useState(null);
  const [datasetFile, setDatasetFile] = useState(null);
  
  const modelInputRef = useRef(null);
  const datasetInputRef = useRef(null);

  const handleLoadDemo = async () => {
    try {
      setLoading(true);
      const data = await loadDemo();
      setPreview(data);
      setDemoLoaded(true);
    } catch (err) {
      alert("Error loading demo: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadFiles = async () => {
    if (!modelFile || !datasetFile) return;
    try {
      setLoading(true);
      const data = await uploadFiles(modelFile, datasetFile);
      setPreview(data);
      setDemoLoaded(true); // Treat as loaded for UI purposes
    } catch (err) {
      alert("Error uploading files: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-header">
        <h2 className="text-xl">Upload & Setup</h2>
        <p className="text-sm text-gray-400">Upload your model and dataset, or load the built-in demo case study.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card hover:border-primary/50 cursor-pointer flex flex-col items-center justify-center py-12" onClick={() => modelInputRef.current.click()}>
          <UploadCloud size={48} className="text-secondary mb-4 opacity-70" />
          <h3 className="text-lg font-heading mb-2">Upload Model</h3>
          <p className="text-sm text-gray-400 text-center px-4">Upload a .pkl model file.</p>
          <input type="file" className="hidden" ref={modelInputRef} accept=".pkl" onChange={(e) => setModelFile(e.target.files[0])} />
          {modelFile && <p className="text-emerald-400 text-sm mt-2 font-bold">{modelFile.name}</p>}
          <button className={`mt-4 px-4 py-2 ${modelFile ? 'bg-primary/20 text-primary border-primary' : 'bg-surface border-border text-gray-500'} border rounded-lg text-sm transition-colors`}>
            {modelFile ? 'Selected' : 'Select File'}
          </button>
        </div>
        <div className="card hover:border-primary/50 cursor-pointer flex flex-col items-center justify-center py-12" onClick={() => datasetInputRef.current.click()}>
          <Database size={48} className="text-primary mb-4 opacity-70" />
          <h3 className="text-lg font-heading mb-2">Upload Dataset</h3>
          <p className="text-sm text-gray-400 text-center px-4">Upload a .csv dataset file containing features and target.</p>
          <input type="file" className="hidden" ref={datasetInputRef} accept=".csv" onChange={(e) => setDatasetFile(e.target.files[0])} />
          {datasetFile && <p className="text-emerald-400 text-sm mt-2 font-bold">{datasetFile.name}</p>}
          <button className={`mt-4 px-4 py-2 ${datasetFile ? 'bg-primary/20 text-primary border-primary' : 'bg-surface border-border text-gray-500'} border rounded-lg text-sm transition-colors`}>
             {datasetFile ? 'Selected' : 'Select File'}
          </button>
        </div>
      </div>
      
      {modelFile && datasetFile && !demoLoaded && (
        <div className="flex justify-center animate-slide-up">
           <button 
              onClick={handleUploadFiles}
              disabled={loading}
              className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-primary hover:from-emerald-400 hover:to-cyan-400 text-background font-bold px-8 py-3 rounded-xl transition-transform hover:scale-105 shadow-xl shadow-primary/20"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <UploadCloud size={20} />
              )}
              {loading ? 'Uploading & Processing...' : 'Process Uploaded Files'}
            </button>
        </div>
      )}

      <div className="flex items-center gap-4 py-4">
        <div className="h-px bg-border flex-1"></div>
        <span className="text-gray-500 text-sm font-semibold uppercase tracking-wider">Or Use Built-in</span>
        <div className="h-px bg-border flex-1"></div>
      </div>

      <div className="card border-primary/30 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="flex items-start justify-between relative z-10">
          <div>
            <h3 className="text-xl font-heading mb-2 text-white flex items-center gap-2">
              <Settings className="text-primary" /> Loan Approval Case Study
            </h3>
            <p className="text-gray-400 mb-6 max-w-2xl">
              Load a pre-trained loan approval model and dataset. This model has intentional biases against certain demographic groups for demonstration purposes.
            </p>
            <button 
              onClick={handleLoadDemo}
              disabled={loading}
              className="flex items-center gap-2 bg-gradient-to-r from-primary to-secondary hover:from-cyan-400 hover:to-violet-400 text-background font-bold px-6 py-3 rounded-xl transition-transform hover:scale-105"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Rocket size={20} />
              )}
              {loading ? 'Loading Demo...' : 'Load Demo Workspace'}
            </button>
          </div>
          
          {demoLoaded && (
            <div className="bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-lg border border-emerald-500/20 flex items-center gap-2 animate-bounce">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              Demo Loaded Successfully
            </div>
          )}
        </div>
      </div>

      {preview && (
        <div className="card animate-slide-up mt-6">
          <h3 className="text-lg font-heading mb-4 text-white">Dataset Preview</h3>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="metric-card !p-4">
              <h3>Model Name</h3>
              <div className="val text-xl">{preview.model_name}</div>
            </div>
            <div className="metric-card !p-4">
              <h3>Total Rows</h3>
              <div className="val text-xl">{preview.rows.toLocaleString()}</div>
            </div>
            <div className="metric-card !p-4">
              <h3>Features</h3>
              <div className="val text-xl">{preview.columns}</div>
            </div>
          </div>
          
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm text-left">
              <thead className="bg-surface text-gray-400 font-medium">
                <tr>
                  {Object.keys(preview.preview[0] || {}).map(k => (
                    <th key={k} className="px-4 py-3 border-b border-border">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {preview.preview.slice(0, 5).map((row, i) => (
                  <tr key={i} className="hover:bg-surface/50">
                    {Object.values(row).map((val, j) => (
                      <td key={j} className="px-4 py-2 text-gray-300 truncate max-w-[150px]">{String(val)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button 
              onClick={() => navigate('/bias')}
              className="bg-surface2 hover:bg-surface border border-primary text-primary px-6 py-2 rounded-lg transition-colors font-medium flex items-center gap-2"
            >
              Proceed to Bias Analysis →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
