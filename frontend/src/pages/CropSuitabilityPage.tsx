import React, { useState, useEffect } from 'react';
import {
  Layers,
  AlertTriangle,
  Sparkles,
  Loader2,
  Thermometer,
  CloudRain,
  Droplets,
  MapPin,
  RefreshCw,
  Search,
  CheckCircle2,
  Info
} from 'lucide-react';
import { ReportAnalysis, CropSuitabilityResponse, WeatherData } from '../types';
import { api } from '../services/api';

interface CropSuitabilityPageProps {
  analysis: ReportAnalysis;
}

export const CropSuitabilityPage: React.FC<CropSuitabilityPageProps> = ({ analysis }) => {
  const [cropData, setCropData] = useState<CropSuitabilityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Weather state
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherMessage, setWeatherMessage] = useState<string | null>(null);
  const [cityInput, setCityInput] = useState('');
  const [showCitySearch, setShowCitySearch] = useState(false);

  // User input states for environmental factors (initially empty or default)
  const [temperature, setTemperature] = useState<number | ''>(24.0);
  const [humidity, setHumidity] = useState<number | ''>(75.0);
  const [rainfall, setRainfall] = useState<number | ''>(150.0);

  // Extract N, P, K, pH from report
  const getReportParam = (name: string): number | undefined => {
    const p = analysis.parameters.find((param) => param.name.toUpperCase() === name.toUpperCase());
    return p?.value ?? undefined;
  };

  const initialN = getReportParam('N') ?? 80;
  const initialP = getReportParam('P') ?? 45;
  const initialK = getReportParam('K') ?? 40;
  const initialPH = getReportParam('pH') ?? 6.5;

  const [nVal, setNVal] = useState<number | ''>(initialN);
  const [pVal, setPVal] = useState<number | ''>(initialP);
  const [kVal, setKVal] = useState<number | ''>(initialK);
  const [phVal, setPhVal] = useState<number | ''>(initialPH);

  // Initial call with soil parameters to verify baseline suitability requirements
  useEffect(() => {
    const fetchInitialStatus = async () => {
      try {
        setLoading(true);
        const res = await api.getCropRecommendations(analysis.report_id, {
          N: typeof nVal === 'number' ? nVal : undefined,
          P: typeof pVal === 'number' ? pVal : undefined,
          K: typeof kVal === 'number' ? kVal : undefined,
          ph: typeof phVal === 'number' ? phVal : undefined,
        });
        setCropData(res);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialStatus();
  }, [analysis.report_id]);

  // Request device geolocation & fetch OpenWeather
  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      setWeatherMessage('Geolocation is not supported by your browser. Please search by city or enter weather values manually.');
      setShowCitySearch(true);
      return;
    }

    setWeatherLoading(true);
    setWeatherMessage('Requesting device location...');

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          setWeatherMessage('Fetching current conditions from OpenWeather...');
          const data = await api.getWeather({ lat, lon });
          
          if (data.available) {
            setWeatherData(data);
            if (data.temperature !== null && data.temperature !== undefined) setTemperature(data.temperature);
            if (data.humidity !== null && data.humidity !== undefined) setHumidity(data.humidity);
            if (data.rainfall !== null && data.rainfall !== undefined) setRainfall(data.rainfall);
            setWeatherMessage(null);
          } else {
            setWeatherMessage(data.message || 'Live weather currently unavailable. You may enter climate factors manually.');
            setShowCitySearch(true);
          }
        } catch (err: any) {
          setWeatherMessage(err.message || 'Failed to fetch weather data.');
          setShowCitySearch(true);
        } finally {
          setWeatherLoading(false);
        }
      },
      (geoError) => {
        setWeatherLoading(false);
        let msg = 'Location access was declined or unavailable. You can search by city name or enter values manually below.';
        if (geoError.code === geoError.TIMEOUT) {
          msg = 'Location request timed out. Please enter your city or weather values manually.';
        }
        setWeatherMessage(msg);
        setShowCitySearch(true);
      },
      { timeout: 10000, enableHighAccuracy: false }
    );
  };

  // Search weather by city
  const handleCitySearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cityInput.trim()) return;

    try {
      setWeatherLoading(true);
      setWeatherMessage(null);
      const data = await api.getWeather({ city: cityInput.trim() });
      if (data.available) {
        setWeatherData(data);
        if (data.temperature !== null && data.temperature !== undefined) setTemperature(data.temperature);
        if (data.humidity !== null && data.humidity !== undefined) setHumidity(data.humidity);
        if (data.rainfall !== null && data.rainfall !== undefined) setRainfall(data.rainfall);
      } else {
        setWeatherMessage(data.message || 'Could not find weather for the specified location. Please enter values manually.');
      }
    } catch (err: any) {
      setWeatherMessage(err.message || 'Error connecting to weather service.');
    } finally {
      setWeatherLoading(false);
    }
  };

  const handlePredict = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getCropRecommendations(analysis.report_id, {
        N: typeof nVal === 'number' ? nVal : undefined,
        P: typeof pVal === 'number' ? pVal : undefined,
        K: typeof kVal === 'number' ? kVal : undefined,
        ph: typeof phVal === 'number' ? phVal : undefined,
        temperature: typeof temperature === 'number' ? temperature : undefined,
        humidity: typeof humidity === 'number' ? humidity : undefined,
        rainfall: typeof rainfall === 'number' ? rainfall : undefined,
      });
      setCropData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to compute crop recommendations.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-6 space-y-8">
      {/* Header Banner */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-800">
                <Layers className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-black text-stone-900 tracking-tight">Crop Recommendation</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-stone-100 text-stone-700 border border-stone-200">
                Agronomic Suitability
              </span>
            </div>
            <p className="text-sm text-stone-600 mt-2 max-w-3xl leading-relaxed">
              Evaluates regional crop suitability across 22 field and specialty crops by combining your lab-measured soil chemistry with local climate variables.
            </p>
          </div>
          <div className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-stone-100 border border-stone-200 text-stone-700">
            Decision Model: ExtraTrees Classifier
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
          {error}
        </div>
      )}

      {/* Weather Integration Card */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-stone-900 flex items-center space-x-2">
              <CloudRain className="w-4 h-4 text-emerald-700" />
              <span>Regional Weather &amp; Climate Sync</span>
            </h3>
            <p className="text-xs text-stone-500 mt-0.5">
              Sync live regional weather to automatically populate temperature, humidity, and rainfall.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleDetectLocation}
              disabled={weatherLoading}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-700 transition shadow-xs disabled:opacity-50 cursor-pointer"
            >
              {weatherLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Detecting...</span>
                </>
              ) : (
                <>
                  <MapPin className="w-3.5 h-3.5" />
                  <span>Detect My Location Weather</span>
                </>
              )}
            </button>

            <button
              onClick={() => setShowCitySearch(!showCitySearch)}
              className="px-3 py-2 rounded-xl text-xs font-semibold bg-stone-100 text-stone-700 hover:bg-stone-200 transition"
            >
              {showCitySearch ? 'Hide City Search' : 'Search City'}
            </button>
          </div>
        </div>

        {/* City Search Form */}
        {showCitySearch && (
          <form onSubmit={handleCitySearch} className="flex gap-2 max-w-md pt-2">
            <input
              type="text"
              value={cityInput}
              onChange={(e) => setCityInput(e.target.value)}
              placeholder="Enter city (e.g. Coimbatore, Fresno, Des Moines)"
              className="flex-1 px-3 py-2 text-xs rounded-xl border border-stone-300 focus:outline-emerald-500 bg-stone-50"
            />
            <button
              type="submit"
              disabled={weatherLoading || !cityInput.trim()}
              className="inline-flex items-center space-x-1 px-3 py-2 rounded-xl text-xs font-bold bg-stone-900 text-white hover:bg-stone-800 disabled:opacity-50 cursor-pointer"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Search</span>
            </button>
          </form>
        )}

        {/* Weather Status Notice */}
        {weatherMessage && (
          <div className="p-3.5 rounded-2xl bg-stone-50 border border-stone-200 text-xs text-stone-700 flex items-start space-x-2">
            <Info className="w-4 h-4 text-stone-500 shrink-0 mt-0.5" />
            <span className="leading-relaxed">{weatherMessage}</span>
          </div>
        )}

        {/* Live Weather Display */}
        {weatherData?.available && (
          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/80 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="font-bold text-emerald-950 flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Live Conditions for: <b>{weatherData.location}</b></span>
              </span>
              <span className="text-stone-500">
                Source: <b>{weatherData.source || 'OpenWeather'}</b>
                {weatherData.timestamp && ` · ${new Date(weatherData.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-1">
              <div className="bg-white p-3 rounded-xl border border-emerald-100 text-center">
                <span className="text-[11px] font-semibold text-stone-500 uppercase">Temperature</span>
                <div className="text-lg font-black text-stone-900 mt-0.5">{weatherData.temperature}°C</div>
              </div>
              <div className="bg-white p-3 rounded-xl border border-emerald-100 text-center">
                <span className="text-[11px] font-semibold text-stone-500 uppercase">Humidity</span>
                <div className="text-lg font-black text-stone-900 mt-0.5">{weatherData.humidity}%</div>
              </div>
              <div className="bg-white p-3 rounded-xl border border-emerald-100 text-center">
                <span className="text-[11px] font-semibold text-stone-500 uppercase">Rainfall</span>
                <div className="text-lg font-black text-stone-900 mt-0.5">{weatherData.rainfall} mm</div>
              </div>
            </div>

            <p className="text-[11px] text-stone-500 italic">
              {weatherData.disclaimer || 'Current weather has been populated below. You can adjust values for seasonal planning if desired.'}
            </p>
          </div>
        )}
      </div>

      {/* Missing Inputs Honest Notification */}
      {cropData?.status === 'INSUFFICIENT_INPUTS' && (
        <div className="p-6 rounded-3xl bg-amber-50/80 border border-amber-200 shadow-xs space-y-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-amber-900">
                Climate Parameters Required for Accurate Recommendation
              </h4>
              <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                A soil laboratory test quantifies soil chemistry (N, P, K, pH) but not atmospheric weather.
                SoilTwin AI never fabricates weather assumptions. Use the weather sync tool above or enter
                regional values below to generate recommendations.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="font-semibold text-amber-900">Required Variables:</span>
            {cropData.missing_inputs?.map((field, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded-md bg-amber-200/80 text-amber-900 font-mono font-bold">
                {field}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Input Parameters Form */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
        <div>
          <h3 className="text-base font-bold text-stone-900">Crop Recommendation Parameters</h3>
          <p className="text-xs text-stone-500">
            Soil values are extracted from your report. Environmental variables can be live-synced or manually fine-tuned.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Soil Values */}
          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1">Nitrogen (N ppm)</label>
            <input
              type="number"
              value={nVal}
              onChange={(e) => setNVal(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500 bg-stone-50"
              placeholder="e.g. 80"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1">Phosphorus (P ppm)</label>
            <input
              type="number"
              value={pVal}
              onChange={(e) => setPVal(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500 bg-stone-50"
              placeholder="e.g. 45"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1">Potassium (K ppm)</label>
            <input
              type="number"
              value={kVal}
              onChange={(e) => setKVal(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500 bg-stone-50"
              placeholder="e.g. 40"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1">Soil pH</label>
            <input
              type="number"
              step="0.1"
              value={phVal}
              onChange={(e) => setPhVal(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500 bg-stone-50"
              placeholder="e.g. 6.5"
            />
          </div>

          {/* Environmental Values */}
          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1 flex items-center space-x-1">
              <Thermometer className="w-3.5 h-3.5 text-rose-500" />
              <span>Temperature (°C)</span>
            </label>
            <input
              type="number"
              step="0.5"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500"
              placeholder="e.g. 24.0"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1 flex items-center space-x-1">
              <Droplets className="w-3.5 h-3.5 text-sky-500" />
              <span>Relative Humidity (%)</span>
            </label>
            <input
              type="number"
              step="1"
              value={humidity}
              onChange={(e) => setHumidity(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500"
              placeholder="e.g. 75"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-stone-600 mb-1 flex items-center space-x-1">
              <CloudRain className="w-3.5 h-3.5 text-indigo-500" />
              <span>Rainfall (mm)</span>
            </label>
            <input
              type="number"
              step="5"
              value={rainfall}
              onChange={(e) => setRainfall(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-xl border border-stone-300 focus:outline-emerald-500"
              placeholder="e.g. 150"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handlePredict}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-sm bg-stone-900 text-white hover:bg-emerald-700 transition shadow-sm disabled:opacity-50 flex items-center justify-center space-x-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-emerald-300" />
                  <span>Generate Recommendations</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Prediction Results */}
      {cropData?.status === 'READY' && cropData.predictions && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
            <div>
              <h3 className="text-lg font-extrabold text-stone-900">Recommended Crops for Your Soil</h3>
              <p className="text-xs text-stone-500">
                Ranked by suitability score using verified soil nutrients and regional climate parameters.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {cropData.predictions.map((pred, idx) => (
                <div
                  key={idx}
                  className="bg-stone-50 border border-stone-200 rounded-2xl p-5 space-y-3 relative overflow-hidden"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-stone-400">
                        Rank #{idx + 1}
                      </span>
                      <h4 className="text-xl font-black text-stone-900">{pred.crop}</h4>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-black text-emerald-700">
                        {(pred.probability * 100).toFixed(1)}%
                      </div>
                      <span className="text-[10px] text-stone-500 font-medium">Suitability Score</span>
                    </div>
                  </div>

                  {/* Probability Bar */}
                  <div className="w-full bg-stone-200 rounded-full h-2">
                    <div
                      className="bg-emerald-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${pred.probability * 100}%` }}
                    ></div>
                  </div>

                  <p className="text-[11px] text-stone-500 italic border-t border-stone-200 pt-2">
                    {pred.disclaimer}
                  </p>
                </div>
              ))}
            </div>

            {/* Plain-Language Suitability Explanation */}
            {cropData.explanation && (
              <div className="p-4 rounded-2xl bg-emerald-50/50 border border-emerald-100 text-xs text-stone-800 space-y-1">
                <span className="font-bold text-emerald-900 uppercase tracking-wider text-[10px]">
                  Agronomic Rationale:
                </span>
                <p className="leading-relaxed">{cropData.explanation}</p>
              </div>
            )}

            {/* Transparent Limitations */}
            {cropData.limitations && (
              <div className="space-y-2 pt-4 border-t border-stone-100 text-[11px] text-stone-500">
                <span className="font-semibold text-stone-700">Guidance &amp; Limitations:</span>
                <ul className="list-disc pl-5 space-y-1">
                  {cropData.limitations.map((lim, idx) => (
                    <li key={idx}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

