import React, { useState } from 'react';
import { UploadCloud, FileCheck, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { ReportAnalysis } from '../types';

interface UploadPageProps {
  onAnalysisComplete: (analysis: ReportAnalysis) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onAnalysisComplete }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    const validExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    const hasValidExt = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExt) {
      setError('Please upload a valid PDF or image file (.pdf, .png, .jpg).');
      setSelectedFile(null);
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError('File exceeds 15 MB limit.');
      setSelectedFile(null);
      return;
    }

    setError(null);
    setSelectedFile(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      setError(null);

      // 1. Upload file
      const uploadRes = await api.uploadReport(selectedFile);

      setUploading(false);
      setAnalyzing(true);

      // 2. Trigger Supervisor Analysis
      const analysisRes = await api.analyzeReport(uploadRes.report_id);
      setAnalyzing(false);

      onAnalysisComplete(analysisRes);
    } catch (err: any) {
      setError(err.message || 'An error occurred during report analysis.');
      setUploading(false);
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-stone-900 tracking-tight">Upload Soil Report</h2>
        <p className="text-sm text-stone-600">
          Upload your digital or scanned soil testing laboratory report (PDF, JPG, PNG).
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start space-x-3 text-rose-800 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Box */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-3xl p-10 text-center transition-all bg-white ${
          dragOver ? 'border-emerald-500 bg-emerald-50/30' : 'border-stone-300 hover:border-emerald-400'
        }`}
      >
        <input
          type="file"
          id="file-upload"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          disabled={uploading || analyzing}
        />
        <div className="space-y-4 pointer-events-none">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-inner">
            <UploadCloud className="w-8 h-8" />
          </div>
          <div>
            <p className="text-base font-semibold text-stone-900">
              Drag &amp; drop PDF / JPG / PNG here
            </p>
            <p className="text-xs text-stone-500 mt-1">or click to browse from your device</p>
          </div>
          <span className="inline-block text-[11px] text-stone-400 font-medium">
            Supported formats: PDF, PNG, JPG (up to 15 MB)
          </span>
        </div>
      </div>

      {/* Selected File Card */}
      {selectedFile && (
        <div className="flex items-center justify-between p-4 bg-white border border-stone-200 rounded-2xl shadow-xs">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="p-2.5 rounded-xl bg-stone-100 text-stone-700">
              <FileCheck className="w-5 h-5 text-emerald-600" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-stone-900 truncate">{selectedFile.name}</p>
              <p className="text-xs text-stone-500">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · {selectedFile.type || 'Document'}
              </p>
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={uploading || analyzing}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-sm font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm disabled:opacity-50 cursor-pointer"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing your soil report...</span>
              </>
            ) : (
              <span>Analyze Report</span>
            )}
          </button>
        </div>
      )}

      {/* Analysis Loading Status */}
      {analyzing && (
        <div className="bg-white border border-stone-200 rounded-3xl p-8 text-center space-y-4 shadow-xs animate-in fade-in duration-300">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-base font-bold text-stone-900">Analyzing your soil report...</h3>
            <p className="text-xs text-stone-500">Extracting measurements and preparing your soil health assessment.</p>
          </div>
        </div>
      )}
    </div>
  );
};
