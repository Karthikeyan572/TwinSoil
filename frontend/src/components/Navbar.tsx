import React from 'react';
import { Sprout, FileText, Sparkles, BookOpen, Layers } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onTryDemo: () => void;
  isDemoLoading: boolean;
  hasReport: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onTryDemo,
  isDemoLoading,
  hasReport,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-stone-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div
            className="flex items-center space-x-3 cursor-pointer"
            onClick={() => setActiveTab('home')}
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-700/20">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-stone-900">SoilTwin AI</span>
                <span className="text-xs px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-medium">v1.0</span>
              </div>
              <p className="text-xs text-stone-500 hidden sm:block">Understand Your Soil. Backed by Evidence.</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('home')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'home'
                  ? 'bg-emerald-50 text-emerald-800'
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
              }`}
            >
              Home
            </button>

            {hasReport && (
              <>
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'dashboard'
                      ? 'bg-emerald-50 text-emerald-800'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Soil Health</span>
                </button>

                <button
                  onClick={() => setActiveTab('evidence')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'evidence'
                      ? 'bg-emerald-50 text-emerald-800'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
                  }`}
                >
                  <BookOpen className="w-4 h-4" />
                  <span>Evidence Citations</span>
                </button>

                <button
                  onClick={() => setActiveTab('crops')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'crops'
                      ? 'bg-emerald-50 text-emerald-800'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>Crop Recommendation</span>
                </button>

                <button
                  onClick={() => setActiveTab('ask')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'ask'
                      ? 'bg-emerald-50 text-emerald-800'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  <span>Ask Soil AI</span>
                </button>
              </>
            )}
          </nav>

          {/* Quick Action: Try Demo */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onTryDemo}
              disabled={isDemoLoading}
              className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-semibold bg-stone-900 text-white hover:bg-emerald-700 transition shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4 text-emerald-300" />
              <span>{isDemoLoading ? 'Loading Demo...' : 'Try Demo Soil Report'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
