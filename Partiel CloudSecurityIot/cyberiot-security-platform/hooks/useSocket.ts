
import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { MetricPayload, DeviceType } from '../types';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [latestMetric, setLatestMetric] = useState<MetricPayload | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Attempt real connection
    try {
      socketRef.current = io({
        path: '/socket.io',
        transports: ['websocket'],
        timeout: 5000,
      });

      socketRef.current.on('connect', () => {
        setIsConnected(true);
        console.log('Real-time monitoring stream online');
      });

      socketRef.current.on('disconnect', () => {
        setIsConnected(false);
      });

      socketRef.current.on('metrics_live', (data: MetricPayload) => {
        setLatestMetric(data);
      });
    } catch (e) {
      console.warn('Socket connection failed');
    }

    return () => {
      if (socketRef.current) socketRef.current.disconnect();
    };
  }, []);

  return { isConnected, latestMetric };
};
