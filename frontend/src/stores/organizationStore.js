import { create } from 'zustand';
import { organizationsAPI } from '../lib/api';

const useOrganizationStore = create((set, get) => ({
  organizations: [],
  currentOrganization: null,
  loading: false,
  error: null,

  // Fetch all organizations
  fetchOrganizations: async () => {
    set({ loading: true, error: null });
    try {
      const response = await organizationsAPI.list();
      set({ organizations: response.data, loading: false });
      
      // If there's a saved organization ID, set it as current
      const savedOrgId = localStorage.getItem('current_organization_id');
      if (savedOrgId) {
        const org = response.data.find(o => o.id === savedOrgId);
        if (org) {
          set({ currentOrganization: org });
        }
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Failed to fetch organizations';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Create new organization
  createOrganization: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await organizationsAPI.create(data);
      const newOrg = response.data;
      
      set((state) => ({
        organizations: [...state.organizations, newOrg],
        loading: false,
      }));
      
      return newOrg;
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Failed to create organization';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Set current organization
  setCurrentOrganization: (organization) => {
    localStorage.setItem('current_organization_id', organization.id);
    set({ currentOrganization: organization });
  },

  // Switch organization
  switchOrganization: async (organizationId) => {
    const org = get().organizations.find(o => o.id === organizationId);
    if (org) {
      get().setCurrentOrganization(org);
      return org;
    } else {
      // Fetch if not in list
      try {
        const response = await organizationsAPI.get(organizationId);
        get().setCurrentOrganization(response.data);
        return response.data;
      } catch (error) {
        throw new Error('Organization not found');
      }
    }
  },

  // Update organization
  updateOrganization: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const response = await organizationsAPI.update(id, data);
      const updatedOrg = response.data;
      
      set((state) => ({
        organizations: state.organizations.map(o => 
          o.id === id ? updatedOrg : o
        ),
        currentOrganization: state.currentOrganization?.id === id 
          ? updatedOrg 
          : state.currentOrganization,
        loading: false,
      }));
      
      return updatedOrg;
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Failed to update organization';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Clear current organization
  clearCurrentOrganization: () => {
    localStorage.removeItem('current_organization_id');
    set({ currentOrganization: null });
  },

  // Clear all
  clearOrganizations: () => {
    localStorage.removeItem('current_organization_id');
    set({
      organizations: [],
      currentOrganization: null,
      error: null,
    });
  },

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useOrganizationStore;