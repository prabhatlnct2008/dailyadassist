import { useState, useEffect } from 'react';
import { Button } from '../shared/Button';
import { Select } from '../shared/Select';
import { pagesApi } from '../../api/pages';

const TONE_OPTIONS = [
  { value: 'friendly', label: 'Friendly' },
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'informative', label: 'Informative' },
];

const CTA_STYLE_OPTIONS = [
  { value: 'direct', label: 'Direct' },
  { value: 'subtle', label: 'Subtle' },
  { value: 'question', label: 'Question-based' },
  { value: 'urgency', label: 'Urgency-driven' },
];

const TARGET_MARKET_OPTIONS = [
  { value: 'b2b', label: 'B2B' },
  { value: 'b2c', label: 'B2C' },
  { value: 'local', label: 'Local' },
  { value: 'national', label: 'National' },
  { value: 'international', label: 'International' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'service', label: 'Service-based' },
];

export function PageSettingsDrawer({ isOpen, onClose, workspaceId, pageId, page }) {
  const [settings, setSettings] = useState({
    default_tone: '',
    default_cta_style: '',
    target_markets: [],
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (page) {
      setSettings({
        default_tone: page.default_tone || '',
        default_cta_style: page.default_cta_style || '',
        target_markets: page.target_markets || [],
      });
    }
  }, [page]);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      await pagesApi.updatePageSettings(workspaceId, pageId, settings);

      onClose(true); // Pass true to indicate success
    } catch (err) {
      console.error('Error saving page settings:', err);
      setError(err.response?.data?.error || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const toggleTargetMarket = (market) => {
    setSettings((prev) => ({
      ...prev,
      target_markets: prev.target_markets.includes(market)
        ? prev.target_markets.filter((m) => m !== market)
        : [...prev.target_markets, market],
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity"
        onClick={() => onClose(false)}
      />

      {/* Drawer */}
      <div className="absolute inset-y-0 right-0 max-w-md w-full bg-white shadow-xl flex flex-col animate-slide-in-right">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Page Settings</h2>
            <button
              onClick={() => onClose(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          {page && (
            <p className="mt-2 text-sm text-gray-500">
              {page.facebook_page?.name}
            </p>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            {/* Default Tone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Tone
              </label>
              <Select
                value={settings.default_tone}
                onChange={(e) =>
                  setSettings({ ...settings, default_tone: e.target.value })
                }
                className="w-full"
              >
                <option value="">Select tone...</option>
                {TONE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
              <p className="mt-1 text-xs text-gray-500">
                The default tone for ad copy generated for this page
              </p>
            </div>

            {/* CTA Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CTA Style
              </label>
              <Select
                value={settings.default_cta_style}
                onChange={(e) =>
                  setSettings({ ...settings, default_cta_style: e.target.value })
                }
                className="w-full"
              >
                <option value="">Select CTA style...</option>
                {CTA_STYLE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
              <p className="mt-1 text-xs text-gray-500">
                The style of call-to-action to use in ads
              </p>
            </div>

            {/* Target Markets */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Markets
              </label>
              <div className="space-y-2">
                {TARGET_MARKET_OPTIONS.map((option) => (
                  <label
                    key={option.value}
                    className="flex items-center space-x-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={settings.target_markets.includes(option.value)}
                      onChange={() => toggleTargetMarket(option.value)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">{option.label}</span>
                  </label>
                ))}
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Select all markets that apply to this page
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4">
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => onClose(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} loading={saving}>
              Save Settings
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PageSettingsDrawer;
