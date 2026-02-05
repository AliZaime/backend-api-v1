
export type DeviceType = 'temperature' | 'humidity' | 'light' | 'pressure' | 'system';
export type DeviceStatus = 'active' | 'inactive';

export interface Device {
  id: number;
  device_id: string;
  name: string;
  type: DeviceType;
  location: string;
  status: DeviceStatus;
  owner_id: number;
  mqtt_topic: string;
  lastSeen?: string;
}

export interface SystemValue {
  cpu_percent: number;
  ram_percent: number;
}

export interface MetricPayload {
  device_id: string;
  value: number | SystemValue;
  unit: string;
  type: DeviceType;
  timestamp: string;
}

export interface User {
  sub: string;
  id: string;
  role?: string;
}

export interface AuthResponse {
  token: string;
  payload: User;
}
