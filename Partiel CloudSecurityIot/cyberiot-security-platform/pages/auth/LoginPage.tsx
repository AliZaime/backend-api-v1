
import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, Eye, EyeOff, Loader2, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('test@gmail.com');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isNetworkError, setIsNetworkError] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setIsNetworkError(false);
    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      if (!err.response) {
        setError('NETWORK ERROR: BACKEND UPLINK OFFLINE');
        setIsNetworkError(true);
      } else {
        setError('AUTHENTICATION FAILED: ACCESS DENIED');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemoMode = async () => {
    setLoading(true);
    await login({ email }, true);
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#020617] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_30%,rgba(34,211,238,0.05)_0%,transparent_60%)]" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[520px] relative z-10"
      >
        <div className="text-center mb-12">
            <div className="inline-block relative mb-8">
                <div className="absolute inset-0 bg-cyan-500/20 blur-2xl rounded-full" />
                <div className="relative z-10 p-5 rounded-[1.5rem] border-2 border-cyan-500/30 bg-[#020617] shadow-[0_0_30px_rgba(34,211,238,0.2)]">
                    <Shield className="text-white w-10 h-10" strokeWidth={1.5} />
                </div>
            </div>
            <h1 className="text-[56px] font-black text-white tracking-[-0.05em] leading-none mb-4 uppercase">
              SENTINEL<span className="text-cyan-400">.</span>IO
            </h1>
            <p className="text-slate-500 font-medium uppercase tracking-[0.4em] text-[11px] opacity-80">
              Security Operations Terminal
            </p>
        </div>

        <div className="bg-[#0b1120]/80 backdrop-blur-xl rounded-[2.5rem] p-12 border border-white/5 shadow-2xl relative">
            <AnimatePresence mode="wait">
              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="mb-8 p-6 bg-[#1a0a0f] border border-[#3d141d] rounded-2xl flex flex-col items-center"
                >
                  <p className="text-[#ff4d4d] text-[11px] font-black uppercase tracking-[0.15em] text-center mb-4">
                    {error}
                  </p>
                  {isNetworkError && (
                    <button 
                      type="button"
                      onClick={handleDemoMode}
                      className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 text-[10px] font-bold uppercase hover:bg-cyan-500/20 transition-all active:scale-95"
                    >
                      <Zap size={14} />
                      Proceed in Demo Mode (Mock Data)
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <form className="space-y-4" onSubmit={handleLogin}>
                <div className="space-y-4">
                    <div className="relative group">
                        <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-cyan-400 transition-colors" size={20} strokeWidth={1.5} />
                        <input 
                            required
                            type="email" 
                            placeholder="admin@sentinel.io"
                            className="w-full bg-[#040816] border border-white/5 rounded-2xl pl-14 pr-6 py-5 text-white text-lg font-semibold focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-700"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="relative group">
                        <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-cyan-400 transition-colors" size={20} strokeWidth={1.5} />
                        <input 
                            required
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••••••"
                            className="w-full bg-[#040816] border border-white/5 rounded-2xl pl-14 pr-14 py-5 text-white text-lg font-semibold tracking-widest focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-700"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button 
                            type="button" 
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-600 hover:text-white transition-colors"
                        >
                            {showPassword ? <EyeOff size={20} strokeWidth={1.5} /> : <Eye size={20} strokeWidth={1.5} />}
                        </button>
                    </div>
                </div>

                <button 
                    disabled={loading}
                    type="submit"
                    className="w-full h-20 mt-4 bg-cyan-400 text-[#020617] font-black text-xl rounded-[1.5rem] hover:bg-cyan-300 transition-all shadow-[0_10px_40px_rgba(34,211,238,0.2)] flex items-center justify-center gap-4 active:scale-[0.98] disabled:opacity-50"
                >
                    {loading ? (
                      <Loader2 className="animate-spin" size={24} />
                    ) : (
                      <>
                        AUTHORIZE UPLINK
                        <ArrowRight size={24} strokeWidth={2.5} />
                      </>
                    )}
                </button>
            </form>

            <div className="mt-10 text-center">
                <p className="text-slate-500 text-[13px] font-medium">
                    Need new credentials? <Link to="/register" className="text-cyan-400 font-bold hover:text-cyan-300 transition-colors">Register Identity</Link>
                </p>
            </div>
        </div>

        <p className="mt-16 text-center text-slate-700 text-[10px] font-bold tracking-[0.2em] uppercase opacity-50">
            Secure Layer: v2.4.0 / TLS 1.3 Active
        </p>
      </motion.div>
    </div>
  );
};

export default LoginPage;
