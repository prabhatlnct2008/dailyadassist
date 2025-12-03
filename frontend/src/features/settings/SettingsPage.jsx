import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { userApi } from '../../api/user';
import { Button } from '../shared/Button';
import { Input } from '../shared/Input';
import { Select } from '../shared/Select';
import { Loader } from '../shared/Loader';

export function SettingsPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [preferences, setPreferences] = useState(null);
  const [adAccounts, setAdAccounts] = useState([]);
  const [pages, setPages] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [prefsData, accountsData, pagesData] = await Promise.all([
        userApi.getPreferences(),
        userApi.getAdAccounts(),
        userApi.getPages(),
      ]);
      setPreferences(prefsData);
      setAdAccounts(accountsData);
      setPages(pagesData);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await userApi.updatePreferences(preferences);
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {/* Account Section */}
        <section className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account</h2>
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-200 rounded-full overflow-hidden">
              {user?.profile_picture_url && (
                <img src={user.profile_picture_url} alt="" className="w-full h-full object-cover" />
              )}
            </div>
            <div>
              <p className="font-medium text-gray-900">{user?.name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Button variant="danger" size="sm" onClick={handleLogout}>
              Sign Out
            </Button>
          </div>
        </section>

        {/* Facebook Connection */}
        <section className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Facebook Connection</h2>

          <div className="space-y-4">
            <div>
              <label className="label">Ad Account</label>
              <Select
                value={adAccounts.find((a) => a.is_primary)?.id || ''}
                onChange={(e) => userApi.setPrimaryAdAccount(e.target.value).then(loadData)}
                options={adAccounts.map((acc) => ({
                  value: acc.id,
                  label: `${acc.name} (${acc.currency})`,
                }))}
              />
            </div>

            <div>
              <label className="label">Facebook Page</label>
              <Select
                value={pages.find((p) => p.is_primary)?.id || ''}
                onChange={(e) => userApi.setPrimaryPage(e.target.value).then(loadData)}
                options={pages.map((page) => ({
                  value: page.id,
                  label: page.name,
                }))}
              />
            </div>
          </div>
        </section>

        {/* Preferences */}
        <section className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferences</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Default Daily Budget"
                type="number"
                value={preferences?.default_daily_budget || 50}
                onChange={(e) =>
                  setPreferences({ ...preferences, default_daily_budget: parseFloat(e.target.value) })
                }
              />
              <Select
                label="Currency"
                value={preferences?.default_currency || 'USD'}
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
              label="Default Tone"
              value={preferences?.default_tone || 'friendly'}
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
              label="Default Objective"
              value={preferences?.default_objective || 'conversions'}
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

            <Select
              label="Timezone"
              value={preferences?.timezone || 'UTC'}
              onChange={(e) =>
                setPreferences({ ...preferences, timezone: e.target.value })
              }
              options={[
                { value: 'UTC', label: 'UTC' },
                { value: 'America/New_York', label: 'Eastern Time' },
                { value: 'America/Los_Angeles', label: 'Pacific Time' },
                { value: 'Europe/London', label: 'London' },
                { value: 'Asia/Kolkata', label: 'India' },
              ]}
            />
          </div>

          <div className="mt-6">
            <Button onClick={handleSave} loading={isSaving}>
              Save Changes
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}

export default SettingsPage;
