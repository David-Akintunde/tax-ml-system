import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, AlertTriangle, TrendingUp, LogOut, LayoutDashboard, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { logout } = useAuth();

  return (
    <div className="w-64 bg-blue-900 text-white flex flex-col">
      <div className="p-4 text-2xl font-bold border-b border-blue-800">FIRSTaxPortal</div>
      <nav className="flex-1 mt-6">
        <NavLink
          to="/dashboard"
          end
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 hover:bg-blue-800 transition ${isActive ? 'bg-blue-800' : ''}`
          }
        >
          <LayoutDashboard size={20} /> Dashboard Home
        </NavLink>
        <NavLink
          to="/dashboard/risk"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 hover:bg-blue-800 transition ${isActive ? 'bg-blue-800' : ''}`
          }
        >
          <Home size={20} /> Risk Assessment
        </NavLink>
        <NavLink
          to="/dashboard/fraud"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 hover:bg-blue-800 transition ${isActive ? 'bg-blue-800' : ''}`
          }
        >
          <AlertTriangle size={20} /> Fraud Detection
        </NavLink>
        <NavLink
          to="/dashboard/forecast"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 hover:bg-blue-800 transition ${isActive ? 'bg-blue-800' : ''}`
          }
        >
          <TrendingUp size={20} /> Revenue Forecast
        </NavLink>
        {/* Profile Link */}
        <NavLink
          to="/dashboard/profile"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 hover:bg-blue-800 transition ${isActive ? 'bg-blue-800' : ''}`
          }
        >
          <User size={20} /> My Profile
        </NavLink>
      </nav>
      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 border-t border-blue-800 hover:bg-blue-800 transition"
      >
        <LogOut size={20} /> Logout
      </button>
    </div>
  );
};

export default Sidebar;