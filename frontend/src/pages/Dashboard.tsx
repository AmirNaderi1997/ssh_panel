import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  Server,
  Cpu,
  TrendingUp,
  Globe,
  Lock,
  Calendar,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Percent,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import client from '../api/client';
import { useNotificationStore } from '../store/notificationStore';

// Default / Mock stats data to ensure UI displays nicely
const defaultStats = {
  users: { total: 0, active: 0, online: 0, expired: 0, disabled: 0 },
  servers: { total: 0, online: 0, offline: 0 },
  system: { cpu_percent: 0.0, ram_percent: 0.0, disk_percent: 0.0, load_avg: [0.0, 0.0, 0.0] },
  domains_total: 0,
  ssl_active: 0,
  ssl_expired: 0,
  revenue_this_month: 0.0,
  daily_registrations: {},
};

export const Dashboard: React.FC = () => {
  const { addToast } = useNotificationStore();

  // Fetch Stats
  const { data: stats = defaultStats, error: statsError } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const res = await client.get('/dashboard/stats');
      return res.data;
    },
    refetchInterval: 10000, // Refresh stats every 10 seconds
  });

  // Fetch Charts Data
  const { data: charts = { traffic_usage: [], user_growth: [], server_load: [], revenue_trends: [] } } = useQuery({
    queryKey: ['dashboard-charts'],
    queryFn: async () => {
      const res = await client.get('/dashboard/charts');
      return res.data;
    },
  });

  useEffect(() => {
    if (statsError) {
      addToast('Error loading real-time dashboard statistics. Showing offline data.', 'error', 5000);
    }
  }, [statsError, addToast]);

  const cards = [
    {
      name: 'SSH VPN Users',
      value: stats.users.total,
      sub: `${stats.users.online} Active Online`,
      icon: <Users className="w-6 h-6 text-primary-500" />,
      color: 'border-l-4 border-primary-500',
    },
    {
      name: 'Active Servers',
      value: `${stats.servers.online} / ${stats.servers.total}`,
      sub: `${stats.servers.offline} Servers Offline`,
      icon: <Server className="w-6 h-6 text-emerald-500" />,
      color: 'border-l-4 border-emerald-500',
    },
    {
      name: 'Revenue (Month)',
      value: `$${stats.revenue_this_month.toFixed(2)}`,
      sub: 'Allocated Credits',
      icon: <TrendingUp className="w-6 h-6 text-amber-500" />,
      color: 'border-l-4 border-amber-500',
    },
    {
      name: 'Domains / SSL',
      value: `${stats.domains_total} Domains`,
      sub: `${stats.ssl_active} SSL Active`,
      icon: <Globe className="w-6 h-6 text-sky-500" />,
      color: 'border-l-4 border-sky-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Dashboard</h1>
        <p className="text-sm text-slate-500 dark:text-dark-text-muted mt-1">
          Real-time insight and overview of tunneling nodes and traffic usage.
        </p>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => (
          <div
            key={card.name}
            className={`bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm flex items-center justify-between ${card.color}`}
          >
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                {card.name}
              </span>
              <p className="text-2xl font-bold text-slate-800 dark:text-white">{card.value}</p>
              <span className="text-xs text-slate-500 dark:text-dark-text-muted font-medium block">
                {card.sub}
              </span>
            </div>
            <div className="p-3 bg-slate-50 dark:bg-dark-input rounded-xl">{card.icon}</div>
          </div>
        ))}
      </div>

      {/* System Resources & Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CPU/RAM/Disk Progress Panel */}
        <div className="lg:col-span-2 bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Local Panel Host Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CPU */}
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-slate-600 dark:text-slate-300">CPU Usage</span>
                <span className="font-bold text-slate-800 dark:text-white">{stats.system.cpu_percent}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-dark-input rounded-full h-3">
                <div
                  className="bg-primary-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${stats.system.cpu_percent}%` }}
                ></div>
              </div>
            </div>
            {/* RAM */}
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-slate-600 dark:text-slate-300">RAM Usage</span>
                <span className="font-bold text-slate-800 dark:text-white">{stats.system.ram_percent}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-dark-input rounded-full h-3">
                <div
                  className="bg-emerald-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${stats.system.ram_percent}%` }}
                ></div>
              </div>
            </div>
            {/* Disk */}
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-slate-600 dark:text-slate-300">Disk Usage</span>
                <span className="font-bold text-slate-800 dark:text-white">{stats.system.disk_percent}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-dark-input rounded-full h-3">
                <div
                  className="bg-amber-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${stats.system.disk_percent}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Load Average widget */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Load Average</h2>
          <div className="flex items-center justify-around text-center py-2">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase">1 Min</p>
              <p className="text-xl font-bold text-slate-800 dark:text-white mt-1">
                {stats.system.load_avg[0]}
              </p>
            </div>
            <div className="w-[1px] h-8 bg-slate-200 dark:bg-dark-border"></div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase">5 Min</p>
              <p className="text-xl font-bold text-slate-800 dark:text-white mt-1">
                {stats.system.load_avg[1]}
              </p>
            </div>
            <div className="w-[1px] h-8 bg-slate-200 dark:bg-dark-border"></div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase">15 Min</p>
              <p className="text-xl font-bold text-slate-800 dark:text-white mt-1">
                {stats.system.load_avg[2]}
              </p>
            </div>
          </div>
          <span className="text-[10px] text-slate-400 text-center font-medium block">
            System load values for host scheduler thread pool.
          </span>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Area Chart */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Traffic Usage (Upload/Download)</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts.traffic_usage}>
                <defs>
                  <linearGradient id="colorRx" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorTx" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${(val / (1024 * 1024)).toFixed(0)}M`} />
                <Tooltip formatter={(value: any) => [`${(value / (1024 * 1024)).toFixed(1)} MB`]} />
                <Legend />
                <Area type="monotone" name="Download (Rx)" dataKey="download_bytes" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorRx)" />
                <Area type="monotone" name="Upload (Tx)" dataKey="upload_bytes" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorTx)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* User Growth Line Chart */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Registered VPN Accounts Growth</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={charts.user_growth}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Legend />
                <Line type="monotone" name="Total Users" dataKey="total_users" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Server Load Bar Chart */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Remote Servers Load Metrics</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.server_load}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="server_name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${val}%`} />
                <Tooltip formatter={(value) => [`${value}%`]} />
                <Legend />
                <Bar name="CPU Utilization" dataKey="cpu_percent" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar name="RAM Utilization" dataKey="ram_percent" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue Trends Chart */}
        <div className="bg-white dark:bg-dark-card border border-slate-200/50 dark:border-dark-border/50 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-6">Reseller Credit Revenue Trends</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.revenue_trends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `$${val}`} />
                <Tooltip formatter={(value) => [`$${value}`]} />
                <Legend />
                <Bar name="Allocated Amount" dataKey="amount" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
