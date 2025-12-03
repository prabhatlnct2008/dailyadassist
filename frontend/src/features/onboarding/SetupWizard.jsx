import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { onboardingApi } from '../../api/onboarding';
import { userApi } from '../../api/user';
import { authApi } from '../../api/auth';
import { Button } from '../shared/Button';
import { Select } from '../shared/Select';
import { Input } from '../shared/Input';
import { Loader } from '../shared/Loader';

const STEPS = [
  { id: 1, title: 'Connect Facebook', description: 'Link your Facebook account' },
  { id: 2, title: 'Select Ad Account', description: 'Choose which account to manage' },
  { id: 3, title: 'Select Page', description: 'Pick your Facebook Page' },
  { id: 4, title: 'Set Defaults', description: 'Configure your preferences' },
];

export function SetupWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [status, setStatus] = useState(null);

  // Data for each step
  const [adAccounts, setAdAccounts] = useState([]);
  const [pages, setPages] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [selectedPage, setSelectedPage] = useState('');
  const [preferences, setPreferences] = useState({
    default_daily_budget: 50,
    default_currency: 'USD',
    default_tone: 'friendly',
    default_objective: 'conversions',
  });

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await onboardingApi.getStatus();
      setStatus(data);
      setCurrentStep(data.current_step);

      if (data.is_complete) {
        navigate('/');
      }
    } catch (error) {
      console.error('Failed to load status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectFacebook = () => {
    window.location.href = authApi.getFacebookConnectUrl();
  };

  const handleFetchAccounts = async () => {
    setIsLoading(true);
    try {
      await onboardingApi.fetchAdAccounts();
      const accounts = await userApi.getAdAccounts();
      setAdAccounts(accounts);
      if (accounts.length > 0) {
        setSelectedAccount(accounts[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAccount = async () => {
    if (!selectedAccount) return;
    setIsLoading(true);
    try {
      await userApi.setPrimaryAdAccount(selectedAccount);
      await onboardingApi.fetchPages();
      const pagesList = await userApi.getPages();
      setPages(pagesList);
      if (pagesList.length > 0) {
        setSelectedPage(pagesList[0].id);
      }
      setCurrentStep(3);
    } catch (error) {
      console.error('Failed to select account:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPage = async () => {
    if (!selectedPage) return;
    setIsLoading(true);
    try {
      await userApi.setPrimaryPage(selectedPage);
      setCurrentStep(4);
    } catch (error) {
      console.error('Failed to select page:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    setIsLoading(true);
    try {
      await userApi.updatePreferences(preferences);
      await onboardingApi.complete();
      navigate('/');
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !status) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {STEPS.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                    currentStep >= step.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {currentStep > step.id ? '✓' : step.id}
                </div>
                {index < STEPS.length - 1 && (
                  <div
                    className={`w-16 h-1 mx-2 ${
                      currentStep > step.id ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-600">
            Step {currentStep} of {STEPS.length}: {STEPS[currentStep - 1]?.title}
          </p>
        </div>

        {/* Step Content */}
        <div className="card p-8">
          {/* Step 1: Connect Facebook */}
          {currentStep === 1 && (
            <div className="text-center">
              <div className="w-16 h-16 bg-facebook-blue rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold mb-2">Connect Your Facebook Account</h2>
              <p className="text-gray-600 mb-6">
                We'll sync your ad data and manage campaigns for you.
              </p>
              <Button variant="facebook" size="lg" onClick={handleConnectFacebook}>
                Connect Facebook
              </Button>
            </div>
          )}

          {/* Step 2: Select Ad Account */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">Choose Your Ad Account</h2>
              <p className="text-gray-600 mb-6">
                We'll focus on this account for now. You can change it later.
              </p>

              {adAccounts.length === 0 ? (
                <div className="text-center py-8">
                  <Button onClick={handleFetchAccounts} loading={isLoading}>
                    Fetch Ad Accounts
                  </Button>
                </div>
              ) : (
                <>
                  <Select
                    label="Ad Account"
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    options={adAccounts.map((acc) => ({
                      value: acc.id,
                      label: `${acc.name} (${acc.facebook_account_id})`,
                    }))}
                  />
                  <div className="mt-6 flex justify-end">
                    <Button onClick={handleSelectAccount} loading={isLoading}>
                      Continue
                    </Button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Step 3: Select Page */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">Choose Your Facebook Page</h2>
              <p className="text-gray-600 mb-6">
                This page will be used for your ad campaigns.
              </p>

              <Select
                label="Facebook Page"
                value={selectedPage}
                onChange={(e) => setSelectedPage(e.target.value)}
                options={pages.map((page) => ({
                  value: page.id,
                  label: page.name,
                }))}
              />

              <div className="mt-6 flex justify-between">
                <Button variant="secondary" onClick={() => setCurrentStep(2)}>
                  Back
                </Button>
                <Button onClick={handleSelectPage} loading={isLoading}>
                  Continue
                </Button>
              </div>
            </div>
          )}

          {/* Step 4: Set Defaults */}
          {currentStep === 4 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">Set Your Preferences</h2>
              <p className="text-gray-600 mb-6">
                Configure default settings for your campaigns.
              </p>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Default Daily Budget"
                    type="number"
                    value={preferences.default_daily_budget}
                    onChange={(e) =>
                      setPreferences({ ...preferences, default_daily_budget: parseFloat(e.target.value) })
                    }
                  />
                  <Select
                    label="Currency"
                    value={preferences.default_currency}
                    onChange={(e) =>
                      setPreferences({ ...preferences, default_currency: e.target.value })
                    }
                    options={[
                      { value: 'USD', label: 'USD ($)' },
                      { value: 'EUR', label: 'EUR (€)' },
                      { value: 'GBP', label: 'GBP (£)' },
                      { value: 'INR', label: 'INR (₹)' },
                    ]}
                  />
                </div>

                <Select
                  label="Default Tone of Voice"
                  value={preferences.default_tone}
                  onChange={(e) =>
                    setPreferences({ ...preferences, default_tone: e.target.value })
                  }
                  options={[
                    { value: 'friendly', label: 'Friendly' },
                    { value: 'professional', label: 'Professional' },
                    { value: 'bold', label: 'Bold' },
                    { value: 'casual', label: 'Casual' },
                  ]}
                />

                <Select
                  label="Default Campaign Objective"
                  value={preferences.default_objective}
                  onChange={(e) =>
                    setPreferences({ ...preferences, default_objective: e.target.value })
                  }
                  options={[
                    { value: 'conversions', label: 'Conversions' },
                    { value: 'traffic', label: 'Traffic' },
                    { value: 'engagement', label: 'Engagement' },
                    { value: 'awareness', label: 'Brand Awareness' },
                  ]}
                />
              </div>

              <div className="mt-6 flex justify-between">
                <Button variant="secondary" onClick={() => setCurrentStep(3)}>
                  Back
                </Button>
                <Button onClick={handleSavePreferences} loading={isLoading}>
                  Finish Setup
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SetupWizard;
