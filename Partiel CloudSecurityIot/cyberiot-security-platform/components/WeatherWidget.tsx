
import React, { useState, useEffect } from 'react';
import { Cloud, Sun, Wind, Droplets, MapPin, Eye, Thermometer } from 'lucide-react';
import { motion } from 'framer-motion';

const WeatherWidget: React.FC = () => {
  const [temp, setTemp] = useState(24.5);
  const [humidity, setHumidity] = useState(62);
  const [wind, setWind] = useState(12.4);

  // Simulation de fluctuations atmosphériques
  useEffect(() => {
    const interval = setInterval(() => {
      setTemp(t => +(t + (Math.random() - 0.5) * 0.2).toFixed(1));
      setHumidity(h => +(h + (Math.random() - 0.5) * 0.5).toFixed(0));
      setWind(w => +(w + (Math.random() - 0.5) * 0.3).toFixed(1));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-card rounded-[2.5rem] p-8 border-white/5 h-full relative overflow-hidden group">
      {/* Background Radar Animation */}
      <div className="absolute top-[-10%] right-[-10%] w-64 h-64 border border-cyan-500/10 rounded-full pointer-events-none group-hover:border-cyan-500/20 transition-colors">
         <div className="absolute inset-0 border border-cyan-500/5 rounded-full scale-75 animate-ping opacity-20" />
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-1 bg-cyan-500 rounded-full shadow-[0_0_10px_#22d3ee]" />
      </div>

      <div className="flex flex-col md:flex-row justify-between h-full relative z-10">
        <div className="flex-1 space-y-6">
          <div className="flex items-center gap-2 text-slate-500">
             <MapPin size={16} className="text-cyan-400" />
             <span className="text-[10px] font-black uppercase tracking-[0.2em]">Deployment Zone: Sector 07 / NE-TK</span>
          </div>

          <div className="flex items-end gap-4">
             <div className="text-7xl font-mono font-bold text-white tracking-tighter">
                {temp}<span className="text-cyan-400 text-3xl">°C</span>
             </div>
             <div className="pb-3">
                <div className="flex items-center gap-2 text-emerald-400">
                   <Sun size={20} />
                   <span className="text-xs font-bold uppercase tracking-widest">Clear Skies</span>
                </div>
                <p className="text-[10px] text-slate-500 font-mono mt-1">FEELS LIKE: 26.1°C</p>
             </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-4">
             <div className="p-4 bg-slate-950/40 rounded-2xl border border-white/5 flex flex-col items-center">
                <Droplets size={18} className="text-blue-400 mb-2" />
                <span className="text-lg font-mono font-bold text-white">{humidity}%</span>
                <span className="text-[8px] text-slate-600 uppercase font-black tracking-widest">Humidity</span>
             </div>
             <div className="p-4 bg-slate-950/40 rounded-2xl border border-white/5 flex flex-col items-center">
                <Wind size={18} className="text-slate-400 mb-2" />
                <span className="text-lg font-mono font-bold text-white">{wind}</span>
                <span className="text-[8px] text-slate-600 uppercase font-black tracking-widest">km/h</span>
             </div>
             <div className="p-4 bg-slate-950/40 rounded-2xl border border-white/5 flex flex-col items-center">
                <Eye size={18} className="text-indigo-400 mb-2" />
                <span className="text-lg font-mono font-bold text-white">12km</span>
                <span className="text-[8px] text-slate-600 uppercase font-black tracking-widest">Visibility</span>
             </div>
          </div>
        </div>

        <div className="md:w-1/3 flex flex-col items-end justify-between mt-8 md:mt-0">
           <div className="bg-slate-950/60 p-4 rounded-3xl border border-white/5 w-full flex items-center justify-between">
              <span className="text-[9px] font-black text-slate-500 uppercase">Air Quality</span>
              <div className="flex items-center gap-2">
                 <span className="text-xs font-mono font-bold text-white">AQI 14</span>
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_5px_#10b981]" />
              </div>
           </div>

           <div className="w-full space-y-2">
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest text-right px-2">Atmospheric Pressure</p>
              <div className="h-20 w-full flex items-end gap-1 px-2">
                 {[40, 60, 45, 80, 50, 70, 55, 65, 90, 40].map((h, i) => (
                    <div 
                      key={i} 
                      className="flex-1 bg-cyan-500/10 rounded-t-sm hover:bg-cyan-500/40 transition-colors" 
                      style={{ height: `${h}%` }}
                    />
                 ))}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default WeatherWidget;
