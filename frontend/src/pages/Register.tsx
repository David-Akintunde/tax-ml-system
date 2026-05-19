import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';


const Register = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [staffId, setStaffId] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const validatePassword = (pwd: string) => {
    if (pwd.length < 8) return 'Minimum 8 characters';
    if (!/[A-Z]/.test(pwd)) return 'Requires uppercase letter';
    if (!/[a-z]/.test(pwd)) return 'Requires lowercase letter';
    if (!/\d/.test(pwd)) return 'Requires a number';
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) return 'Requires special character (!@#$%^&*)';
    return '';
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPwd = e.target.value;
    setPassword(newPwd);
    setErrors(prev => ({ ...prev, password: validatePassword(newPwd) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName || !lastName || !staffId || !email) {
      setErrors({ form: 'All fields are required' });
      return;
    }
    const pwdError = validatePassword(password);
    if (pwdError) {
      setErrors({ password: pwdError });
      return;
    }
    setLoading(true);
    const success = await register(firstName, lastName, staffId, email, password);
    if (success) navigate('/login');
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-600">
      <div className="bg-white p-8 rounded-lg shadow-xl w-96">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-900">Create Account</h1>
          <p className="text-gray-600">Register as FIRS staff</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-gray-700 mb-1">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
                required
              />
            </div>
          </div>
          <div className="mb-3">
            <label className="block text-gray-700 mb-1">Staff ID</label>
            <input
              type="text"
              value={staffId}
              onChange={(e) => setStaffId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
              required
            />
          </div>
          <div className="mb-3">
            <label className="block text-gray-700 mb-1">Email (@firs.gov.ng)</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
              required
            />
          </div>
          <div className="mb-3">
            <label className="block text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={handlePasswordChange}
              className="w-full px-3 py-2 border rounded-lg"
              required
            />
            {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            <div className="text-xs text-gray-500 mt-1">
              Requirements: min 8 chars, uppercase, lowercase, number, special char
            </div>
          </div>
          {errors.form && <p className="text-red-500 text-sm mb-3">{errors.form}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="text-center text-gray-500 text-sm mt-4">
          Already have an account? <Link to="/login" className="text-blue-600">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;