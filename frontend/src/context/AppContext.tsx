import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ExtractionResult, Profile, SampleJd } from '../types';

interface AppContextType {
  currentStep: number;
  setCurrentStep: (step: number) => void;
  selectedJd: SampleJd | ExtractionResult | null;
  setSelectedJd: (jd: SampleJd | ExtractionResult | null) => void;
  parsedResume: ExtractionResult | null;
  setParsedResume: (res: ExtractionResult | null) => void;
  profileId: string | null;
  setProfileId: (id: string | null) => void;
  company: string;
  setCompany: (comp: string) => void;
  currentProfile: Profile | null;
  setCurrentProfile: (p: Profile | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentStep, setCurrentStep] = useState<number>(3); // Default to Step 3 (Profile) or Step 1
  const [selectedJd, setSelectedJd] = useState<SampleJd | ExtractionResult | null>(null);
  const [parsedResume, setParsedResume] = useState<ExtractionResult | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [company, setCompany] = useState<string>('Stripe');
  const [currentProfile, setCurrentProfile] = useState<Profile | null>(null);

  // Sync company from selectedJd when selected
  useEffect(() => {
    if (selectedJd && 'company' in selectedJd && selectedJd.company) {
      setCompany(selectedJd.company);
    }
  }, [selectedJd]);

  return (
    <AppContext.Provider
      value={{
        currentStep,
        setCurrentStep,
        selectedJd,
        setSelectedJd,
        parsedResume,
        setParsedResume,
        profileId,
        setProfileId,
        company,
        setCompany,
        currentProfile,
        setCurrentProfile,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export function useApp(): AppContextType {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
