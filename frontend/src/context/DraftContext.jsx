import { createContext, useContext, useState, useCallback } from 'react';
import { draftsApi } from '../api/drafts';

const DraftContext = createContext(null);

export function DraftProvider({ children }) {
  const [currentDraft, setCurrentDraft] = useState(null);
  const [variants, setVariants] = useState([]);
  const [selectedVariant, setSelectedVariant] = useState(0);
  const [isEditing, setIsEditing] = useState(false);

  const loadDraft = useCallback(async (id) => {
    try {
      const data = await draftsApi.get(id);
      setCurrentDraft(data);
      return data;
    } catch (error) {
      console.error('Failed to load draft:', error);
      return null;
    }
  }, []);

  const loadVariants = useCallback(async (id) => {
    try {
      const data = await draftsApi.getVariants(id);
      setVariants(data);
      return data;
    } catch (error) {
      console.error('Failed to load variants:', error);
      return [];
    }
  }, []);

  const updateDraft = useCallback(async (id, updates) => {
    try {
      const data = await draftsApi.update(id, updates);
      setCurrentDraft(data);
      return data;
    } catch (error) {
      console.error('Failed to update draft:', error);
      return null;
    }
  }, []);

  const publishDraft = useCallback(async (id) => {
    try {
      const result = await draftsApi.publish(id);
      return result;
    } catch (error) {
      console.error('Failed to publish draft:', error);
      throw error;
    }
  }, []);

  const setPreviewFromAgent = useCallback((previewData) => {
    setCurrentDraft((prev) => ({
      ...prev,
      ...previewData,
    }));
  }, []);

  const value = {
    currentDraft,
    variants,
    selectedVariant,
    isEditing,
    loadDraft,
    loadVariants,
    updateDraft,
    publishDraft,
    setCurrentDraft,
    setPreviewFromAgent,
    setSelectedVariant,
    setIsEditing,
  };

  return (
    <DraftContext.Provider value={value}>{children}</DraftContext.Provider>
  );
}

export function useDraft() {
  const context = useContext(DraftContext);
  if (!context) {
    throw new Error('useDraft must be used within a DraftProvider');
  }
  return context;
}

export default DraftContext;
