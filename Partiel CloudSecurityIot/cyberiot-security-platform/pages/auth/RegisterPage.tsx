
import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';

const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await register({ email, password });
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_0%,rgba(99,102,241,0.1)_0%,transparent_50%)]" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-[480px] relative z-10"
      >
        <div className="text-center mb-10">
            <h1 className="text-4xl font-black text-white tracking-tighter mb-2">CREATE IDENTITY</h1>
            <p className="text-slate-500 uppercase tracking-[0.2em] text-[10px]">Registry Portal / Sentinel.io</p>
        </div>

        <div className="glass-card rounded-[2.5rem] p-10 border-white/5">
            {error && <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl">{error}</div>}
            <form className="space-y-6" onSubmit={handleSubmit}>
                <div className="space-y-4">
                    <div className="relative">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input 
                            required
                            type="email" 
                            placeholder="Email Address"
                            className="w-full bg-slate-950/50 border border-white/10 rounded-2xl pl-12 pr-6 py-4 text-white focus:outline-none focus:border-cyan-500 transition-all"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input 
                            required
                            type="password" 
                            placeholder="Password Key"
                            className="w-full bg-slate-950/50 border border-white/10 rounded-2xl pl-12 pr-6 py-4 text-white focus:outline-none focus:border-cyan-500 transition-all"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                </div>

                <button 
                    disabled={loading}
                    type="submit"
                    className="w-full h-14 bg-white text-slate-950 font-bold rounded-2xl hover:bg-cyan-400 transition-all flex items-center justify-center gap-3 active:scale-95 disabled:opacity-50"
                >
                    {loading ? 'PROCESSING...' : 'COMPLETE ENROLLMENT'}
                    <UserPlus size={18} />
                </button>
            </form>

            <div className="mt-8 text-center">
                <p className="text-slate-500 text-xs">
                    Already registered? <Link to="/login" className="text-cyan-400 font-bold hover:underline">Return to Uplink</Link>
                </p>
            </div>
        </div>
      </motion.div>
    </div>
  );
};

export default RegisterPage;
