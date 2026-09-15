import React, { useState } from 'react';
import { Sparkles, Send, BookOpen, CheckCircle2, Loader2, Bot, User } from 'lucide-react';
import { ReportAnalysis, ChatResponse } from '../types';
import { api } from '../services/api';

interface AskSoilAIPageProps {
  analysis: ReportAnalysis;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: { source: string; page?: number | null; text: string }[];
}

export const AskSoilAIPage: React.FC<AskSoilAIPageProps> = ({ analysis }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I have analyzed your soil report (ID: ${analysis.report_id}). You can ask me any specific agronomic questions regarding your measured parameters, nutrient deficiencies, pH levels, or soil amendments. My answers are strictly grounded in authoritative university extension science.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    'Why is my potassium deficient and what are the agronomic consequences?',
    'What does my soil pH of 4.5 mean for nutrient availability?',
    'How does organic matter affect water retention in my soil?',
  ];

  const handleSend = async (questionText?: string) => {
    const q = (questionText || input).trim();
    if (!q || loading) return;

    const userMsg: Message = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await api.askSoilAi(analysis.report_id, q);
      const assistantMsg: Message = {
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error while consulting the agricultural knowledge base.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-6 max-w-4xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-stone-900">Ask Soil AI</h2>
            <p className="text-xs text-stone-500">
              Evidence-grounded agronomic consultation strictly scoped to your soil report &amp; extension citations.
            </p>
          </div>
        </div>
      </div>

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
