import React, { useState, useEffect } from 'react';
import { Sparkles, Send, BookOpen, CheckCircle2, Loader2, Bot, User, Key, Check, ExternalLink } from 'lucide-react';
import { ReportAnalysis, ChatResponse } from '../types';
import { api } from '../services/api';

interface AskSoilAIPageProps {
  analysis: ReportAnalysis;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: { source: string; page?: number | null; text: string }[];
  provider?: string;
}

export const AskSoilAIPage: React.FC<AskSoilAIPageProps> = ({ analysis }) => {
  const [geminiApiKey, setGeminiApiKey] = useState<string>(() => {
    return localStorage.getItem('twinsoil_gemini_api_key') || '';
  });
  const [showKeyConfig, setShowKeyConfig] = useState(false);
  const [tempKey, setTempKey] = useState(geminiApiKey);
  const [savedNotice, setSavedNotice] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I am SoilTwin AI powered by Google Gemini and authoritative university extension RAG. I have analyzed your report (ID: ${analysis.report_id}). You can ask me any agronomic questions regarding your measured parameters, nutrient deficiencies, pH levels, or soil amendments.`,
      provider: geminiApiKey ? 'Google Gemini 1.5 Flash' : 'SoilTwin Scientific Engine',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    'Why is my potassium deficient and what are the agronomic consequences?',
    'What does my soil pH of 4.5 mean for nutrient availability?',
    'How does organic matter affect water retention in my soil?',
  ];

  const handleSaveKey = () => {
    const trimmed = tempKey.trim();
    setGeminiApiKey(trimmed);
    if (trimmed) {
      localStorage.setItem('twinsoil_gemini_api_key', trimmed);
    } else {
      localStorage.removeItem('twinsoil_gemini_api_key');
    }
    setSavedNotice(true);
    setTimeout(() => {
      setSavedNotice(false);
      setShowKeyConfig(false);
    }, 1200);
  };

  const handleSend = async (questionText?: string) => {
    const q = (questionText || input).trim();
    if (!q || loading) return;

    const userMsg: Message = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await api.askSoilAi(analysis.report_id, q, geminiApiKey);
      const assistantMsg: Message = {
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        provider: res.provider || (geminiApiKey ? 'Google Gemini 1.5 Flash' : 'SoilTwin Scientific Engine'),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error while consulting the agricultural knowledge base.',
          provider: 'Error Fallback',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-6 max-w-4xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-stone-900">Ask Soil AI</h2>
            <p className="text-xs text-stone-500">
              Evidence-grounded agronomic consultation strictly scoped to your soil report &amp; extension citations.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <span className="w-2 h-2 rounded-full mr-1.5 bg-emerald-500 animate-pulse"></span>
            Google Gemini 1.5 Flash
          </span>
          <button
            onClick={() => setShowKeyConfig(!showKeyConfig)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-stone-200 hover:border-stone-400 text-xs font-medium text-stone-700 bg-stone-50 hover:bg-stone-100 transition cursor-pointer"
          >
            <Key className="w-3.5 h-3.5 text-stone-500" />
            <span>{geminiApiKey ? 'Key Configured' : 'Set Gemini Key'}</span>
          </button>
        </div>
      </div>

      {/* Gemini API Key Config Drawer */}
      {showKeyConfig && (
        <div className="bg-white border border-stone-200 rounded-2xl p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold text-stone-800">
              <Key className="w-4 h-4 text-emerald-600" />
              <span>Google Gemini API Key</span>
            </div>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-emerald-600 hover:underline flex items-center space-x-1"
            >
              <span>Get free key</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="password"
              value={tempKey}
              onChange={(e) => setTempKey(e.target.value)}
              placeholder="Paste AIzaSy... (optional, server default used if empty)"
              className="flex-1 px-3 py-2 text-xs border border-stone-300 rounded-xl font-mono focus:outline-emerald-600"
            />
            <button
              onClick={handleSaveKey}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition flex items-center space-x-1 cursor-pointer"
            >
              {savedNotice ? <Check className="w-3.5 h-3.5" /> : null}
              <span>{savedNotice ? 'Saved!' : 'Save Key'}</span>
            </button>
          </div>
          <p className="text-[11px] text-stone-500 leading-normal">
            Your key is safely stored locally in your browser and used to power live Gemini 1.5 Flash agronomic answers grounded in your soil parameters and extension citations.
          </p>
        </div>
      )}

      {/* Suggested Questions */}
      <div className="flex flex-wrap gap-2">
        {sampleQuestions.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(sq)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-xl bg-white border border-stone-200 text-stone-700 hover:border-emerald-400 hover:text-emerald-800 transition text-left cursor-pointer"
          >
            "{sq}"
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs space-y-6 min-h-[420px] max-h-[600px] overflow-y-auto">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-3 ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                m.role === 'user' ? 'bg-stone-900 text-white' : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {m.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`space-y-2 max-w-xl ${m.role === 'user' ? 'text-right' : ''}`}>
              {m.provider && (
                <div className="text-[10px] font-semibold text-emerald-700 mb-1 flex items-center space-x-1">
                  <Sparkles className="w-3 h-3" />
                  <span>{m.provider}</span>
                </div>
              )}
              <div
                className={`inline-block p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-stone-900 text-white rounded-tr-xs'
                    : 'bg-stone-50 border border-stone-200/80 text-stone-800 rounded-tl-xs'
                }`}
              >
                {m.content}
              </div>

              {/* Source Citations */}
              {m.citations && m.citations.length > 0 && (
                <div className="space-y-2 text-left pt-1">
                  <div className="flex items-center space-x-1.5 text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Supporting Extension Citations</span>
                  </div>
                  {m.citations.map((c, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-3 rounded-xl bg-emerald-50/50 border border-emerald-100 text-xs text-stone-700 space-y-1"
                    >
                      <div className="flex items-center justify-between font-semibold text-emerald-900 text-[11px]">
                        <span>{c.source}</span>
                        {c.page && <span>Page {c.page}</span>}
                      </div>
                      <p className="italic text-[11px] text-stone-600 border-l-2 border-emerald-500 pl-2">
                        "{c.text}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-xs text-stone-500">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center space-x-2 bg-stone-50 border border-stone-200 p-3 rounded-2xl">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
              <span>Retrieving extension citations &amp; formulating response...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center space-x-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your soil report (e.g. Why is my potassium deficient?)..."
          disabled={loading}
          className="flex-1 px-4 py-3 rounded-2xl border border-stone-300 bg-white text-sm focus:outline-emerald-500 shadow-xs"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-3.5 rounded-2xl bg-stone-900 hover:bg-emerald-700 text-white transition shadow-xs disabled:opacity-50 cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
