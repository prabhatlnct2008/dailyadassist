import client from './client';

export const onboardingApi = {
  // Get onboarding status
  getStatus: async () => {
    const response = await client.get('/onboarding/status');
    return response.data;
  },

  // Complete a step
  completeStep: async (step, data = {}) => {
    const response = await client.post('/onboarding/complete-step', { step, ...data });
    return response.data;
  },

  // Fetch ad accounts from Facebook
  fetchAdAccounts: async () => {
    const response = await client.post('/onboarding/complete-step', { step: 'fetch_ad_accounts' });
    return response.data;
  },

  // Fetch pages from Facebook
  fetchPages: async () => {
    const response = await client.post('/onboarding/complete-step', { step: 'fetch_pages' });
    return response.data;
  },

  // Complete onboarding
  complete: async () => {
    const response = await client.post('/onboarding/complete-step', { step: 'complete_onboarding' });
    return response.data;
  },
};

export default onboardingApi;
