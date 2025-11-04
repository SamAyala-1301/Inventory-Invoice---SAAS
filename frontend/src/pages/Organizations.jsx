import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useOrganizationStore from '../stores/organizationStore';
import useAuthStore from '../stores/authStore';

export default function Organizations() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { 
    organizations, 
    fetchOrganizations, 
    createOrganization, 
    setCurrentOrganization,
    loading, 
    error 
  } = useOrganizationStore();
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const handleCreateOrganization = async (e) => {
    e.preventDefault();
    try {
      const newOrg = await createOrganization(formData);
      setShowCreateModal(false);
      setFormData({ name: '', description: '' });
      // Automatically select the new organization
      setCurrentOrganization(newOrg);
      navigate('/dashboard');
    } catch (err) {
      // Error handled by store
    }
  };

  const handleSelectOrganization = (org) => {
    setCurrentOrganization(org);
    navigate('/dashboard');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Inventory SaaS</h1>
            <p className="text-sm text-gray-600">Signed in as {user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Select an Organization
          </h2>
          <p className="text-gray-600">
            Choose an organization to continue, or create a new one
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading organizations...</p>
          </div>
        )}

        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Create New Organization Card */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-primary-500 hover:bg-primary-50 transition text-center group"
            >
              <div className="text-4xl text-gray-400 group-hover:text-primary-600 mb-4">+</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Create New Organization
              </h3>
              <p className="text-sm text-gray-600">
                Start fresh with a new workspace
              </p>
            </button>

            {/* Existing Organizations */}
            {organizations.map((org) => (
              <button
                key={org.id}
                onClick={() => handleSelectOrganization(org)}
                className="bg-white border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 hover:shadow-md transition text-left"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-xl font-bold text-primary-600">
                      {org.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                    {org.user_role}
                  </span>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {org.name}
                </h3>
                
                {org.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {org.description}
                  </p>
                )}
                
                <div className="flex items-center text-xs text-gray-500">
                  <span>{org.member_count} member{org.member_count !== 1 ? 's' : ''}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {!loading && organizations.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">
              You don't belong to any organizations yet.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700"
            >
              Create Your First Organization
            </button>
          </div>
        )}
      </main>

      {/* Create Organization Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Create New Organization
            </h3>
            
            <form onSubmit={handleCreateOrganization} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Acme Corp"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Brief description of your organization"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}