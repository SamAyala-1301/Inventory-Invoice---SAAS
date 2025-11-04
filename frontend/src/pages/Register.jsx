import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../components/AuthLayout';
import useAuthStore from '../stores/authStore';

export default function Register() {
  const navigate = useNavigate();
  const { register, loading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await register(formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err) {
      // Error is handled by store
    }
  };

  if (success) {
    return (
      <AuthLayout title="Registration Successful!">
        <div className="text-center py-8">
          <div className="text-green-600 text-5xl mb-4">✓</div>
          <p className="text-lg mb-4">
            Your account has been created successfully!
          </p>
          <p className="text-gray-600 mb-4">
            Please check your email to verify your account.
          </p>
          <p className="text-sm text-gray-500">
            Redirecting to login...
          </p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout 
      title="Create Account" 
      subtitle="Start managing your inventory today"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address *
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password *
          </label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            minLength={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Min. 8 characters"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password *
          </label>
          <input
            type="password"
            name="password_confirm"
            value={formData.password_confirm}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div className="text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
            Sign In
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}