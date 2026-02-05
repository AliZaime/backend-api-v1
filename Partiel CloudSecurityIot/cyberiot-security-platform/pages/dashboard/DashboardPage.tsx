
import React, { useState, useEffect } from 'react';
import axiosClient from '../../services/axiosClient';
import { useSocket } from '../../hooks/useSocket';
import { useAuth } from '../../hooks/useAuth';
import { Device } from '../../types';
import LiveChart from '../../components/LiveChart';
import { ShieldCheck, Zap, Activity, Globe, Database, Cpu, Loader2, CloudRain } from 'lucide-react';
import { motion } from 'framer-motion';

const MOCK_DEVICES: Device[] = [
  { id: 991, device_id: 'mock-uuid-1', name: 'Alpha-Reactor-Temp', type: 'temperature', location: 'Section A1', status: 'active', owner_id: 1, mqtt_topic: 'test' },
  { id: 992, device_id: 'mock-uuid-2', name: 'Server-Rack-Humid', type: 'humidity', location: 'Data Center 1', status: 'active', owner_id: 1, mqtt_topic: 'test' },
  { id: 993, device_id: 'mock-uuid-3', name: 'Perimeter-Light-04', type: 'light', location: 'External Yard', status: 'inactive', owner_id: 1, mqtt_topic: 'test' },
  { id: 994, device_id: 'mock-uuid-4', name: 'System-Core-Cluster', type: 'system', location: 'Central Vault', status: 'active', owner_id: 1, mqtt_topic: 'test' },
  { id: 995, device_id: 'mock-uuid-5', name: 'Pressure-Valve-99', type: 'pressure', location: 'Maintenance Hub', status: 'active', owner_id: 1, mqtt_topic: 'test' },
];

const DashboardPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const { isConnected, latestMetric } = useSocket();
  const { isDemoMode } = useAuth();

  useEffect(() => {
    const fetch = async () => {
      if (isDemoMode) {
        setDevices(MOCK_DEVICES);
        setLoading(false);
        return;
      }

      try {
        const res = await axiosClient.get<Device[]>('/devices');
        setDevices(res.data);
      } catch (err) {
        setDevices(MOCK_DEVICES);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [isDemoMode]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="animate-spin text-cyan-500" size={40} />
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {/* Sensor Grid */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-8 bg-cyan-500 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.5)]" />
            <h2 className="text-2xl font-bold tracking-tight">Node Cluster Monitoring</h2>
          </div>
          <div className="flex items-center gap-4 bg-slate-900/50 px-4 py-2 rounded-xl border border-white/5">
             <div className="flex items-center gap-2">
               <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-cyan-500 shadow-[0_0_8px_#06b6d4]'}`}></span>
               <span className="text-[10px] font-bold text-slate-400 font-mono tracking-widest uppercase">
                 {isConnected ? 'LIVE FEED ACTIVE' : 'SIMULATED DATA UPLINK'}
               </span>
             </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {devices.map((device) => (
            <LiveChart 
              key={device.device_id} 
              device={device} 
              latestMetric={latestMetric} 
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
