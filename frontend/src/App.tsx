import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { UploadPage } from './pages/UploadPage';
import { SoilDashboardPage } from './pages/SoilDashboardPage';
import { EvidencePage } from './pages/EvidencePage';
import { CropSuitabilityPage } from './pages/CropSuitabilityPage';
import { AskSoilAIPage } from './pages/AskSoilAIPage';
import { ReportAnalysis } from './types';
import { api } from './services/api';
import { ShieldCheck, Sprout } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'home' | 'upload' | 'dashboard' | 'evidence' | 'crops' | 'ask'>('home');
  const [analysis, setAnalysis] = useState<ReportAnalysis | null>(null);
  const [demoLoading, setDemoLoading] = useState(false);

  const handleTryDemo = async () => {
    try {
      setDemoLoading(true);
      const demoData = await api.loadDemoDuffyRear();
      setAnalysis(demoData);
      setActiveTab('dashboard');
    } catch (err: any) {
      alert(`Failed to load demo report: ${err.message}`);
    } finally {
      setDemoLoading(false);
    }
  };

  const handleAnalysisComplete = (data: ReportAnalysis) => {
    setAnalysis(data);
    setActiveTab('dashboard');
  };

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col text-stone-900 font-sans">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab: any) => setActiveTab(tab)}
        onTryDemo={handleTryDemo}
        isDemoLoading={demoLoading}
        hasReport={!!analysis}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        {activeTab === 'home' && (
          <HomePage
            onStartUpload={() => setActiveTab('upload')}
            onTryDemo={handleTryDemo}
            isDemoLoading={demoLoading}
          />
        )}

        {activeTab === 'upload' && (
          <UploadPage onAnalysisComplete={handleAnalysisComplete} />
        )}

        {activeTab === 'dashboard' && analysis && (
          <SoilDashboardPage analysis={analysis} />
        )}

        {activeTab === 'evidence' && analysis && (
          <EvidencePage analysis={analysis} />
        )}

        {activeTab === 'crops' && analysis && (
          <CropSuitabilityPage analysis={analysis} />
        )}

        {activeTab === 'ask' && analysis && (
          <AskSoilAIPage analysis={analysis} />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-stone-200 bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-stone-500">
          <div className="flex items-center space-x-2">
            <Sprout className="w-4 h-4 text-emerald-600" />
            <span className="font-bold text-stone-800">SoilTwin AI</span>
            <span>—</span>
            <span>Understand Your Soil. Backed by Evidence.</span>
          </div>

          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1 text-emerald-800 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Zero-Fabrication Guarantee</span>
            </span>
            <span>·</span>
            <span>LangGraph + PyMuPDF + RAG + Scikit-Learn</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
