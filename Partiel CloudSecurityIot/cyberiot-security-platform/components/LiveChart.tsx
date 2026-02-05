import React, { useEffect, useRef, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions
} from 'chart.js';
import { Device, MetricPayload } from '../types';
import { Thermometer, Droplets, Server, Zap, Gauge } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface LiveChartProps {
  device: Device;
  latestMetric: MetricPayload | null;
}

interface SystemValue {
  cpu_percent: number;
  ram_percent: number;
}

const LiveChart: React.FC<LiveChartProps> = ({ device, latestMetric }) => {
  const chartRef = useRef<ChartJS<'line'>>(null);
  const [active, setActive] = useState(false);
  const [currentCpu, setCurrentCpu] = useState(0);
  const [currentRam, setCurrentRam] = useState(0);
  const [currentValue, setCurrentValue] = useState(0);
  const isInactive = device.status === 'inactive';
  const isSystem = device.type === 'system';

  // Persistent data storage
  const labelsRef = useRef<string[]>([]);
  const cpuDataRef = useRef<number[]>([]);
  const ramDataRef = useRef<number[]>([]);
  const valueDataRef = useRef<number[]>([]);

  // Configuration based on device type
  const config = React.useMemo(() => {
    switch (device.type) {
      case 'temperature': return { icon: Thermometer, color: '#f59e0b', glow: 'rgba(245, 158, 11, 0.2)', unit: '°C' };
      case 'humidity': return { icon: Droplets, color: '#0ea5e9', glow: 'rgba(14, 165, 233, 0.2)', unit: '%' };
      case 'system': return { icon: Server, color: '#10b981', glow: 'rgba(16, 185, 129, 0.2)', unit: '%' };
      case 'light': return { icon: Zap, color: '#facc15', glow: 'rgba(250, 204, 21, 0.2)', unit: 'lx' };
      default: return { icon: Gauge, color: '#22d3ee', glow: 'rgba(34, 211, 238, 0.2)', unit: '' };
    }
  }, [device.type]);

  const Icon = config.icon;

  // Stable chart data object that references our mutable arrays
  const chartData = React.useMemo(() => {
    if (isSystem) {
      return {
        labels: labelsRef.current,
        datasets: [
          {
            label: 'CPU (%)',
            data: cpuDataRef.current,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
          },
          {
            label: 'RAM (%)',
            data: ramDataRef.current,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
          }
        ]
      };
    } else {
      return {
        labels: labelsRef.current,
        datasets: [
          {
            label: device.type,
            data: valueDataRef.current,
            borderColor: config.color,
            backgroundColor: config.glow,
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
          }
        ]
      };
    }
  }, [isSystem, device.type, config]);

  // Handle incoming metrics
  useEffect(() => {
    // CRITICAL: Only process metrics for THIS device
    if (!latestMetric || latestMetric.device_id !== device.device_id) {
      return;
    }

    if (isInactive) {
      return;
    }

    setActive(true);
    const timer = setTimeout(() => setActive(false), 800);

    const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    let rawValue = latestMetric.value;

    // Parse stringified JSON if needed
    if (typeof rawValue === 'string' && rawValue.startsWith('{')) {
      try { rawValue = JSON.parse(rawValue); } catch (e) { /* ignore */ }
    }

    // Update refs (the source of truth)
    labelsRef.current.push(timeLabel);

    if (isSystem && typeof rawValue === 'object' && rawValue !== null) {
      const val = rawValue as any;
      const cpu = val.cpu_percent ?? val.cpu ?? val.cpu_usage ?? 0;
      const ram = val.ram_percent ?? val.ram ?? val.ram_usage ?? val.memory_percent ?? 0;

      setCurrentCpu(cpu);
      setCurrentRam(ram);

      cpuDataRef.current.push(cpu);
      ramDataRef.current.push(ram);
    } else {
      const value = typeof rawValue === 'number' ? rawValue : (typeof rawValue === 'string' ? parseFloat(rawValue) || 0 : 0);
      setCurrentValue(value);
      valueDataRef.current.push(value);
    }

    // Keep only last 50 points
    if (labelsRef.current.length > 50) {
      labelsRef.current.shift();
      cpuDataRef.current.shift();
      ramDataRef.current.shift();
      valueDataRef.current.shift();
    }

    // Force chart update from the updated refs
    const chart = chartRef.current;
    if (chart) {
      chart.update('none');
    }

    return () => clearTimeout(timer);
  }, [latestMetric?.timestamp]);



  const chartOptions: ChartOptions<'line'> = React.useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: false, // Disable chartjs internal animation for smoother streaming
    plugins: {
      legend: {
        display: isSystem,
        labels: {
          color: '#94a3b8',
          boxWidth: 10,
          font: { size: 10 }
        },
        position: 'bottom',
      },
      tooltip: {
        enabled: !isInactive,
        backgroundColor: '#020617',
        borderColor: '#1e293b',
        borderWidth: 1,
        titleColor: '#f8fafc',
        bodyColor: config.color,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}${config.unit}`;
          }
        }
      }
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        ticks: {
          color: '#64748b',
          callback: function(value) {
            return value + (config.unit || '');
          }
        },
        grid: {
          color: '#334155'
        },
        beginAtZero: true,
        max: (isSystem || device.type === 'light' || device.type === 'humidity') ? 100 : undefined,
      }
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  }), [isSystem, isInactive, config, device.type]);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`glass-card rounded-[2rem] p-6 group border border-white/5 hover:border-cyan-500/30 transition-all duration-500 overflow-hidden relative ${isInactive ? 'opacity-50 grayscale-[0.5]' : ''}`}
    >
      {isInactive && (
         <div className="absolute inset-0 bg-slate-950/20 backdrop-blur-[1px] flex items-center justify-center z-20 pointer-events-none">
            <span className="text-[10px] font-black uppercase tracking-[0.5em] text-slate-500 rotate-[-10deg] border border-slate-700 px-4 py-1 rounded">Offline</span>
         </div>
      )}

      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
        <Icon size={80} />
      </div>

      <div className="flex justify-between items-start relative z-10 mb-8">
        <div className="flex gap-4">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center bg-slate-950/50 border border-white/10 group-hover:border-cyan-500/50 transition-colors shadow-inner">
             <Icon size={22} style={{ color: isInactive ? '#475569' : config.color }} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">{device.type} node</h3>
            <p className={`text-lg font-bold transition-colors ${isInactive ? 'text-slate-500' : 'text-white group-hover:text-cyan-400'}`}>{device.name}</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-2">
              <AnimatePresence>
                {active && !isInactive && (
                  <motion.div 
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee]"
                  />
                )}
              </AnimatePresence>
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tighter">{isInactive ? 'Power Down' : 'Live Uplink'}</span>
            </div>
            {isSystem ? (
              <div className="flex gap-4">
                <div className="text-right">
                  <p className="text-[10px] text-slate-500 uppercase font-bold">CPU</p>
                  <p className="text-xl font-mono font-bold" style={{ color: isInactive ? '#475569' : '#38bdf8' }}>
                    {isInactive ? '0.0' : currentCpu.toFixed(1)}%
                  </p>
                </div>
                <div className="text-right border-l border-white/10 pl-4">
                  <p className="text-[10px] text-slate-500 uppercase font-bold">RAM</p>
                  <p className="text-xl font-mono font-bold" style={{ color: isInactive ? '#475569' : '#10b981' }}>
                    {isInactive ? '0.0' : currentRam.toFixed(1)}%
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-2xl font-mono font-bold mt-1" style={{ color: isInactive ? '#475569' : config.color }}>
                {isInactive ? '0.0' : currentValue.toFixed(1)}
                <span className="text-xs ml-1 opacity-50 font-sans">
                    {isInactive ? '---' : config.unit}
                </span>
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="relative z-10 h-[180px]">
        <Line ref={chartRef} data={chartData} options={chartOptions} />
      </div>
    </motion.div>
  );
};

// Wrap with React.memo to prevent unnecessary re-renders
export default React.memo(LiveChart, (prevProps, nextProps) => {
  // Only re-render if device_id changes or if we receive a new metric for THIS device
  if (prevProps.device.device_id !== nextProps.device.device_id) {
    return false; // Props changed, re-render
  }
  
  if (prevProps.device.status !== nextProps.device.status) {
    return false; // Status changed, re-render
  }
  
  // Check if the new metric is for this device
  const isForThisDevice = nextProps.latestMetric?.device_id === nextProps.device.device_id;
  const wasForThisDevice = prevProps.latestMetric?.device_id === prevProps.device.device_id;
  
  // If neither old nor new metric is for this device, don't re-render
  if (!isForThisDevice && !wasForThisDevice) {
    return true; // Props are "equal", skip re-render
  }
  
  // If we have a new metric for this device, re-render
  if (isForThisDevice && prevProps.latestMetric?.timestamp !== nextProps.latestMetric?.timestamp) {
    return false; // New metric for this device, re-render
  }
  
  return true; // Otherwise, skip re-render
});
