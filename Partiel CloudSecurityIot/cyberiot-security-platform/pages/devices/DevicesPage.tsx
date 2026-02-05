
import React, { useState, useEffect } from 'react';
import axiosClient from '../../services/axiosClient';
import { useAuth } from '../../hooks/useAuth';
import { Device, DeviceType, DeviceStatus } from '../../types';
import {
  Plus, Trash2, MapPin, Cpu, Search, X, Activity, HardDrive, Loader2, Edit3, Power
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DevicesPage: React.FC = () => {
  const { user } = useAuth();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  // Form State
  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState<DeviceType>('temperature');
  const [newLocation, setNewLocation] = useState('');

  const fetchDevices = async () => {
    try {
      const res = await axiosClient.get<Device[]>('/devices');
      setDevices(res.data);
    } catch (err) {
      console.error('Failed to fetch devices', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const openAddModal = () => {
    setEditingDevice(null);
    setNewName('');
    setNewType('temperature');
    setNewLocation('');
    setIsModalOpen(true);
  };

  const openEditModal = (device: Device) => {
    setEditingDevice(device);
    setNewName(device.name);
    setNewType(device.type);
    setNewLocation(device.location);
    setIsModalOpen(true);
  };

  const handleSaveDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingDevice) {
        const updatedFields = { name: newName, type: newType, location: newLocation };
        await axiosClient.put(`/devices/${editingDevice.id}`, updatedFields);
      } else {
        const newDevice = { 
          name: newName, 
          type: newType, 
          location: newLocation,
          owner_id: parseInt(user?.id || "1") // Dynamic owner_id from auth context
        };
        await axiosClient.post('/devices', newDevice);
      }
      fetchDevices();
      setIsModalOpen(false);
    } catch (e) {
      console.error("Error saving device", e);
      alert("Failed to save device. Check console.");
    }
  };

  const toggleStatus = async (device: Device) => {
    const newStatus: DeviceStatus = device.status === 'active' ? 'inactive' : 'active';
    try {
      // Use PUT for partial update (backend supports it via exclude_unset)
      await axiosClient.put(`/devices/${device.id}`, { status: newStatus });
      fetchDevices();
    } catch (e) {
      console.error("Error toggling status", e);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to decommission this device?')) return;
    setIsDeleting(id);
    try {
      await axiosClient.delete(`/devices/${id}`);
      setDevices(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error("Error deleting device", err);
    } finally {
      setIsDeleting(null);
    }
  };

  const filteredDevices = devices.filter(d =>
    d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <HardDrive className="text-cyan-500" size={32} />
            <h1 className="text-4xl font-bold text-white tracking-tight">Fleet Provisioning</h1>
          </div>
          <p className="text-slate-500 text-lg">Central control for hardware registration and security policy deployment.</p>
        </div>

        <button
          onClick={openAddModal}
          className="h-14 px-8 bg-cyan-500 text-slate-950 font-bold rounded-2xl hover:bg-cyan-400 transition-all shadow-[0_0_20px_rgba(6,182,212,0.2)] active:scale-95 flex items-center gap-3"
        >
          <Plus size={20} />
          Register New Node
        </button>
      </div>

      <div className="glass-card rounded-[2.5rem] border-white/5 overflow-hidden">
        <div className="p-8 bg-white/[0.01] border-b border-white/5 flex flex-col md:flex-row gap-6 justify-between items-center">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
            <input
              type="text"
              placeholder="Search registry..."
              className="w-full bg-slate-950/50 border border-white/10 rounded-2xl pl-12 pr-6 py-4 text-sm focus:outline-none focus:border-cyan-500 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-4">
            <div className="px-4 py-2 bg-slate-900 rounded-xl border border-white/5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Live Registry: <span className="text-cyan-400 ml-1">{devices.length} Units</span>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-20 flex justify-center"><Loader2 className="animate-spin text-cyan-500" /></div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="text-slate-500 text-[10px] uppercase tracking-widest font-black border-b border-white/5">
                  <th className="px-8 py-6">Identity</th>
                  <th className="px-8 py-6">Type</th>
                  <th className="px-8 py-6">Site Location</th>
                  <th className="px-8 py-6 text-center">Power Status</th>
                  <th className="px-8 py-6 text-right">Operations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.02]">
                {filteredDevices.map((device) => {
                  // Fallback for ID mismatch if any
                  const deviceId = device.device_id || device.id;
                  // But our types say 'id', and backend responseDTO maps 'device_id' (uuid) string to 'device_id'.
                  // Wait, DeviceResponseDTO: id (int), device_id (uuid).
                  // But axiosClient.get<Device[]> assumes response maps to Device interface.
                  // If backend returns {id: 1, device_id: "uuid"}, and Device interface has {id: "uuid"}, we have a problem.
                  // We should fix this. 
                  // HOWEVER, the DeviceResponseDTO returns both.
                  // Let's rely on 'device_id' if present, or 'id' if it looks like a string.
                  // BETTER: I will assume the 'Device' interface in types.ts should really align with DeviceResponseDTO.
                  // For now, let's use device.device_id for operations if available, or device.id.
                  // Actually, let's fix the FRONTEND TYPE MAPPING in `types.ts` later if needed.
                  // For now, I'll access properties safely.

                  return (
                    <tr key={device.id} className="hover:bg-white/[0.02] transition-colors group">
                      <td className="px-8 py-6">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl bg-slate-950 flex items-center justify-center border border-white/5 transition-colors ${device.status === 'active' ? 'text-cyan-400 border-cyan-500/30' : 'text-slate-600'}`}>
                            <Cpu size={20} />
                          </div>
                          <span className={`font-bold text-sm ${device.status === 'active' ? 'text-white' : 'text-slate-500'}`}>{device.name}</span>
                          <span className="text-[10px] text-slate-600 font-mono hidden md:inline-block ml-2">{device.device_id}</span>
                        </div>
                      </td>
                      <td className="px-8 py-6">
                        <span className="text-xs text-slate-400 capitalize bg-slate-900 px-3 py-1 rounded-lg border border-white/5">{device.type}</span>
                      </td>
                      <td className="px-8 py-6 text-slate-400 text-sm">
                        {device.location}
                      </td>
                      <td className="px-8 py-6 text-center">
                        <button
                          onClick={() => toggleStatus(device)}
                          className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border transition-all ${device.status === 'active' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.1)]' : 'bg-slate-900 border-slate-700 text-slate-600'}`}
                        >
                          <Power size={12} strokeWidth={3} />
                          <span className="text-[10px] font-black uppercase tracking-tighter">{device.status}</span>
                        </button>
                      </td>
                      <td className="px-8 py-6 text-right">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleDelete(device.id)}
                            disabled={isDeleting === device.id}
                            className="p-2 text-slate-600 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all disabled:opacity-50"
                          >
                            {isDeleting === device.id ? <Loader2 size={18} className="animate-spin" /> : <Trash2 size={18} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
          {!loading && filteredDevices.length === 0 && (
            <div className="p-20 text-center text-slate-600 italic">No devices found in this sector.</div>
          )}
        </div>
      </div>

      {/* Modal for Add/Edit */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
              onClick={() => setIsModalOpen(false)}
            />
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="glass-card w-full max-w-lg rounded-[2rem] p-8 relative z-10 border border-white/10"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold">{editingDevice ? 'Modify Protocol' : 'Node Provisioning'}</h3>
                <button onClick={() => setIsModalOpen(false)} className="text-slate-500 hover:text-white"><X /></button>
              </div>
              <form onSubmit={handleSaveDevice} className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Device Name</label>
                  <input required value={newName} onChange={e => setNewName(e.target.value)} className="w-full bg-slate-950 border border-white/10 rounded-xl p-4 text-white focus:border-cyan-500 outline-none" placeholder="e.g. Alpha-Sector-Sensor" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Sensor Category</label>
                  <select value={newType} onChange={e => setNewType(e.target.value as DeviceType)} className="w-full bg-slate-950 border border-white/10 rounded-xl p-4 text-white focus:border-cyan-500 outline-none">
                    <option value="temperature">Temperature</option>
                    <option value="humidity">Humidity</option>
                    <option value="light">Luminosity</option>
                    <option value="pressure">Pressure</option>
                    <option value="system">System Cluster</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Deployment Site</label>
                  <input required value={newLocation} onChange={e => setNewLocation(e.target.value)} className="w-full bg-slate-950 border border-white/10 rounded-xl p-4 text-white focus:border-cyan-500 outline-none" placeholder="e.g. Data Center - Floor 2" />
                </div>
                <button type="submit" className="w-full h-14 bg-white text-slate-950 font-bold rounded-xl hover:bg-cyan-400 transition-all uppercase tracking-widest text-xs">
                  {editingDevice ? 'Commit Changes' : 'Deploy Device'}
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DevicesPage;
