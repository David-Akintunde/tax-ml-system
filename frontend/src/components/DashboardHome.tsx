import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import axios from 'axios';
import { TrendingUp, AlertTriangle, Users, DollarSign } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import API_BASE_URL from '../api/config';

const DashboardHome = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalTaxpayers: 50000,
    highRiskCount: 0,
    avgAnomaly: 0,
    nextMonthForecast: null as number | null,
    monthlyRevenue: [] as { month: string; revenue: number }[],
    riskDistribution: [] as { name: string; value: number }[],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const monthly = [
          { month: 'Jan', revenue: 1210000 },
          { month: 'Feb', revenue: 1100000 },
          { month: 'Mar', revenue: 1040000 },
          { month: 'Apr', revenue: 980000 },
          { month: 'May', revenue: 830000 },
          { month: 'Jun', revenue: 920000 },
          { month: 'Jul', revenue: 1010000 },
          { month: 'Aug', revenue: 1120000 },
          { month: 'Sep', revenue: 1180000 },
          { month: 'Oct', revenue: 1250000 },
          { month: 'Nov', revenue: 1300000 },
          { month: 'Dec', revenue: 1400000 },
        ];
        
        const highRiskCount = Math.round(50000 * 0.15);
        const avgAnomaly = 0.28;
        const last12 = monthly.map(m => m.revenue);
        const forecastRes = await axios.post(`${API_BASE_URL}/predict/forecast`, { last_12_months: last12 });
        const nextForecast = forecastRes.data.forecast;
        
        const riskDist = [
          { name: 'Low Risk (0-0.3)', value: 30000 },
          { name: 'Medium Risk (0.3-0.6)', value: 12500 },
          { name: 'High Risk (>0.6)', value: 7500 },
        ];
        
        setStats({
          totalTaxpayers: 50000,
          highRiskCount,
          avgAnomaly,
          nextMonthForecast: nextForecast,
          monthlyRevenue: monthly,
          riskDistribution: riskDist,
        });
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

  if (loading) return <div className="flex justify-center items-center h-64"><div className="animate-pulse text-gray-500">Loading dashboard data...</div></div>;

  const greetingName = user?.first_name || 'Officer';

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-700 to-blue-500 rounded-xl shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold">Hey, {greetingName} 👋</h1>
        <p className="text-blue-100 mt-1">Welcome back to FIRS Tax Analytics Dashboard</p>
      </div>

      {/* KPI Cards with hover effects */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-xl transition-transform transform hover:scale-105">
          <div className="flex items-center gap-4">
            <Users className="text-blue-600" size={32} />
            <div>
              <p className="text-gray-500 text-sm">Total Taxpayers</p>
              <p className="text-2xl font-bold">{stats.totalTaxpayers.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-xl transition-transform transform hover:scale-105">
          <div className="flex items-center gap-4">
            <AlertTriangle className="text-red-600" size={32} />
            <div>
              <p className="text-gray-500 text-sm">High Risk</p>
              <p className="text-2xl font-bold">{stats.highRiskCount.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-xl transition-transform transform hover:scale-105">
  <div className="flex items-center gap-4">
    <span className="text-green-600 text-3xl font-bold">₦</span>
    <div>
      <p className="text-gray-500 text-sm">Next Month Forecast</p>
      <p className="text-2xl font-bold">₦{stats.nextMonthForecast?.toLocaleString()}</p>
    </div>
  </div>
</div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-xl transition-transform transform hover:scale-105">
          <div className="flex items-center gap-4">
            <DollarSign className="text-green-600" size={32} />
            <div>
              <p className="text-gray-500 text-sm">Next Month Forecast</p>
              <p className="text-2xl font-bold">₦{stats.nextMonthForecast?.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold mb-4">Monthly Revenue (Last 12 Months)</h3>
          <BarChart width={500} height={300} data={stats.monthlyRevenue}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" fill="#3b82f6" name="Revenue (₦)" />
          </BarChart>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
          <PieChart width={400} height={300}>
            <Pie
              data={stats.riskDistribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : 0}%`}
              outerRadius={80}
              dataKey="value"
            >
              {stats.riskDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>

      {/* Revenue Trend Line */}
      <div className="bg-white p-4 rounded-xl shadow-md">
        <h3 className="text-lg font-semibold mb-4">Revenue Trend (Actual + Forecast)</h3>
        <LineChart width={800} height={300} data={[...stats.monthlyRevenue, { month: 'Next', revenue: stats.nextMonthForecast || 0 }]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="revenue" stroke="#10b981" name="Revenue (₦)" />
        </LineChart>
      </div>
    </div>
  );
};

export default DashboardHome;