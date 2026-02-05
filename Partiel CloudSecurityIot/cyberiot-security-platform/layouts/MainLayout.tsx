
import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  LogOut,
  Activity,
  ChevronRight,
  Zap,
  User as UserIcon
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { motion } from 'framer-motion';

const MainLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/devices', icon: Cpu, label: 'Devices' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl relative z-30">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-cyan-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="text-white w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">
            SENTINEL<span className="text-cyan-400">.</span>IO
          </h1>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                ${isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'}
              `}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
              {window.location.hash.replace('#', '') === item.to && (
                <motion.div layoutId="active-pill" className="ml-auto">
                  <ChevronRight size={16} />
                </motion.div>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 mt-auto border-t border-slate-800/50">
          <div className="bg-slate-800/40 rounded-2xl p-4 mb-4">
            <p className="text-xs text-slate-500 uppercase font-semibold mb-1">Authenticated As</p>
            <p className="text-sm font-medium truncate">{user?.sub}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all duration-200"
          >
            <LogOut size={20} />
            <span className="font-medium">Disconnect</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/3 h-1/3 bg-cyan-500/5 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-blue-600/5 blur-[120px] pointer-events-none" />

        <header className="h-20 border-b border-slate-800/50 bg-slate-950/20 backdrop-blur-md flex items-center justify-between px-8 relative z-20">
          <div className="flex items-center gap-4">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
            <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">System Status: Nominal</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 bg-slate-900/50 px-4 py-2 rounded-xl border border-white/5">
              <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center">
                <UserIcon size={16} className="text-slate-400" />
              </div>
              <span className="text-sm font-bold text-slate-200">{user?.sub || 'Operator'}</span>
            </div>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-8 relative z-10 scroll-smooth">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default MainLayout;
