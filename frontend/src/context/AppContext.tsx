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
  const [currentStep, setCurrentStep] = useState<number>(0); // 0 = Landing Page, 1..5 = Pipeline Stages
  const [selectedJd, setSelectedJd] = useState<SampleJd | ExtractionResult | null>(null);
  const [parsedResume, setParsedResume] = useState<ExtractionResult | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [company, setCompany] = useState<string>('Microsoft Corporation');
  const [currentProfile, setCurrentProfile] = useState<Profile | null>(null);

  // Sync company from selectedJd when selected
  useEffect(() => {
    if (selectedJd && 'company' in selectedJd && selectedJd.company) {
      setCompany(selectedJd.company);
    }
  }, [selectedJd]);

  // Sync parsedResume into currentProfile when available
  useEffect(() => {
    if (parsedResume && parsedResume.skills && parsedResume.skills.length > 0) {
      const extraObj = (parsedResume.extras || {}) as Record<string, any>;
      setCurrentProfile((prev) => ({
        profile_id: prev?.profile_id && prev.profile_id !== 'active-parsed-resume' ? prev.profile_id : 'active-parsed-resume',
        name: extraObj.candidate_name || extraObj.name || (prev?.name && prev.name !== 'Active Candidate' ? prev.name : 'Active Candidate'),
        email: extraObj.email || prev?.email || '',
        education: extraObj.education || prev?.education || '',
        github_url: extraObj.github_url || prev?.github_url || '',
        skills: parsedResume.skills,
        hackathons: prev?.hackathons || [],
        internships: prev?.internships || [],
        certifications: extraObj.certifications || prev?.certifications || [],
        preferred_roles: parsedResume.role ? [parsedResume.role] : prev?.preferred_roles || [],
        cv_file: parsedResume.source_file || prev?.cv_file,
      }));
    }
  }, [parsedResume]);

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
