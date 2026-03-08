import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, Upload, BarChart2, GitMerge, Wrench, FileCheck, Award, Bell } from 'lucide-react';
import Setup from './pages/Setup';
import Bias from './pages/Bias';
import Intersectional from './pages/Intersectional';
import Remediation from './pages/Remediation';
import Compliance from './pages/Compliance';
import Certificate from './pages/Certificate';

const Sidebar = () => {
  const location = useLocation();
  const navItems = [
    { path: '/setup', label: 'Upload & Setup', icon: <Upload size={18} /> },
    { path: '/bias', label: 'Bias Analysis', icon: <BarChart2 size={18} /> },
    { path: '/intersectional', label: 'Intersectional Bias', icon: <GitMerge size={18} /> },
    { path: '/remediation', label: 'Bias Remediation', icon: <Wrench size={18} /> },
    { path: '/compliance', label: 'Compliance Report', icon: <FileCheck size={18} /> },
    { path: '/certificate', label: 'Audit Certificate', icon: <Award size={18} /> },
  ];

  return (
    <div className="w-64 bg-surface h-screen fixed left-0 top-0 border-r border-border text-gray-300 flex flex-col pt-6 z-10 transition-all duration-300">
      <div className="px-6 pb-6 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Shield className="text-primary" size={28} />
          <div>
            <h1 className="text-xl font-heading font-bold text-white tracking-tight">FairGuard AI</h1>
            <p className="text-[11px] text-gray-400 mt-1 uppercase tracking-wider font-semibold">Bias Audit & Correction</p>
          </div>
        </div>
      </div>
      <div className="flex-1 py-6 flex flex-col gap-2 px-4">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
              location.pathname === item.path || (location.pathname === '/' && item.path === '/setup')
                ? 'bg-primary/10 text-primary font-bold shadow-inner'
                : 'hover:bg-surface2 hover:text-white'
            }`}
          >
            <span className={location.pathname === item.path ? 'text-primary' : 'text-gray-400 group-hover:text-white'}>
              {item.icon}
            </span>
            <span className="text-sm">{item.label}</span>
          </Link>
        ))}
      </div>
      <div className="p-6 border-t border-border/50 text-xs text-gray-500 text-center">
        Powered by DeepMind Tech
      </div>
    </div>
  );
};

const Topbar = () => {
  return (
    <div className="h-16 border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-10 flex items-center justify-between px-8 transition-colors">
      <div className="font-heading font-semibold text-lg flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
        API Connected
      </div>
      <div className="flex items-center gap-4">
        <button className="relative p-2 rounded-full hover:bg-surface2 transition-colors">
          <Bell size={18} className="text-gray-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-secondary rounded-full border border-background"></span>
        </button>
        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20">
          U
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Topbar />
        <main className="flex-1 p-8 overflow-x-hidden">
          <Routes>
            <Route path="/" element={<Setup />} />
            <Route path="/setup" element={<Setup />} />
            <Route path="/bias" element={<Bias />} />
            <Route path="/intersectional" element={<Intersectional />} />
            <Route path="/remediation" element={<Remediation />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/certificate" element={<Certificate />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
