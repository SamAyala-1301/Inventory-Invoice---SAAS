import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import AuthLayout from '../components/AuthLayout';
import useAuthStore from '../stores/authStore';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const from = location.state?.from?.pathname || '/organizations';

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await login(formData);
      navigate(from, { replace: true });
    } catch (err) {
      // Error is handled by store
    }
  };

  return (
    <AuthLayout 
      title="Welcome Back" 
      subtitle="Sign in to your account"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            autoComplete="email"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="current-password"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="ml-2 text-gray-600">Remember me</span>
          </label>
          
          <Link 
            to="/forgot-password" 
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </button>

        <div className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
            Create Account
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}