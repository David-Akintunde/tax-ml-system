import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import API_BASE_URL from '../api/config';

const Profile = () => {
  const { token, fetchUser } = useAuth();
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    staff_id: '',
    email: '',
    created_at: '',
  });
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setProfile(res.data);
      } catch (err) {
        toast.error('Failed to load profile');
      }
    };
    loadProfile();
  }, [token]);

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdating(true);
    try {
      await axios.post(`${API_BASE_URL}/auth/change-password`,
        { current_password: currentPassword, new_password: newPassword },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Password updated');
      setCurrentPassword('');
      setNewPassword('');
      await fetchUser();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Update failed');
    }
    setUpdating(false);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">User Profile</h2>
      <div className="space-y-4 mb-8">
        <div><label className="font-semibold">First Name:</label> {profile.first_name}</div>
        <div><label className="font-semibold">Last Name:</label> {profile.last_name}</div>
        <div><label className="font-semibold">Staff ID:</label> {profile.staff_id}</div>
        <div><label className="font-semibold">Email:</label> {profile.email}</div>
        <div><label className="font-semibold">Member Since:</label> {new Date(profile.created_at).toLocaleDateString()}</div>
      </div>
      <hr className="my-6" />
      <h3 className="text-xl font-bold mb-4">Change Password</h3>
      <form onSubmit={handlePasswordUpdate} className="space-y-4">
        <div>
          <label className="block mb-1">Current Password</label>
          <input type="password" className="w-full border rounded p-2" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-1">New Password (min 8 chars, uppercase, lowercase, number, special char)</label>
          <input type="password" className="w-full border rounded p-2" value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
        </div>
        <button type="submit" disabled={updating} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Update Password</button>
      </form>
    </div>
  );
};

export default Profile;