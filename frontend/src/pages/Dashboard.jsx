import { useNavigate } from 'react-router-dom';
import useOrganizationStore from '../stores/organizationStore';
import useAuthStore from '../stores/authStore';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { currentOrganization, clearCurrentOrganization } = useOrganizationStore();

  const handleSwitchOrganization = () => {
    clearCurrentOrganization();
    navigate('/organizations');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!currentOrganization) {
    navigate('/organizations');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">
                {currentOrganization.name}
              </h1>
              <span className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full">
                {currentOrganization.user_role}
              </span>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.full_name || user?.email}</p>
                <p className="text-xs text-gray-600">{user?.email}</p>
              </div>
              
              <button
                onClick={handleSwitchOrganization}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Switch Org
              </button>
              
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard
          </h2>
          <p className="text-gray-600">
            Welcome to your organization dashboard
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Total Products</h3>
              <span className="text-2xl">📦</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">0</p>
            <p className="text-sm text-gray-600 mt-2">No products yet</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Invoices</h3>
              <span className="text-2xl">🧾</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">0</p>
            <p className="text-sm text-gray-600 mt-2">No invoices created</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Team Members</h3>
              <span className="text-2xl">👥</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{currentOrganization.member_count}</p>
            <p className="text-sm text-gray-600 mt-2">Active members</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Revenue</h3>
              <span className="text-2xl">💰</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">$0</p>
            <p className="text-sm text-gray-600 mt-2">This month</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-left">
              <div className="text-3xl mb-2">➕</div>
              <h4 className="font-semibold text-gray-900 mb-1">Add Product</h4>
              <p className="text-sm text-gray-600">Create a new product</p>
            </button>

            <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-left">
              <div className="text-3xl mb-2">📄</div>
              <h4 className="font-semibold text-gray-900 mb-1">New Invoice</h4>
              <p className="text-sm text-gray-600">Create an invoice</p>
            </button>

            <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-left">
              <div className="text-3xl mb-2">👤</div>
              <h4 className="font-semibold text-gray-900 mb-1">Invite Member</h4>
              <p className="text-sm text-gray-600">Add team members</p>
            </button>
          </div>
        </div>

        {/* Getting Started */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            🎉 Getting Started
          </h3>
          <p className="text-gray-700 mb-4">
            Welcome to Sprint 1! This is your multi-tenant dashboard with authentication 
            and organization management fully working.
          </p>
          <div className="space-y-2 text-sm text-gray-700">
            <p>✅ User registration & authentication with JWT</p>
            <p>✅ Organization creation & management</p>
            <p>✅ Role-based access control (RBAC)</p>
            <p>✅ Multi-tenant data isolation</p>
            <p className="text-gray-600 mt-4">
              More features coming in Sprint 2: Products, Inventory, and Invoices!
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}