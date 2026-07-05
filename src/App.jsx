import { useState, useEffect, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const DEFAULT_FORM = {
  origin: "",
  destination: "",
  start_date: "",
  end_date: "",
  budget: "",
  travelers: 1,
  interests: "",
};

const AGENT_STEPS = [
  { name: "Memory Recall Agent", desc: "Accessing user profile and history...", icon: "🧠" },
  { name: "Weather Research Agent", desc: "Fetching current OpenWeather reports...", icon: "🌦️" },
  { name: "Flight search Agent", desc: "Sifting through Amadeus flight listings...", icon: "✈️" },
  { name: "Hotel Search Agent", desc: "Checking Booking.com rates against budget...", icon: "🏨" },
  { name: "Itinerary Builder Agent", desc: "Routing sightseeing points via Google Places...", icon: "🗺️" },
  { name: "Budget Auditor Agent", desc: "Performing cost auditing and optimization...", icon: "💰" },
];

export default function App() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  // Simulated agent pipeline tracker logic during loading state
  useEffect(() => {
    let interval;
    if (loading) {
      setActiveStep(0);
      interval = setInterval(() => {
        setActiveStep((prev) => (prev < AGENT_STEPS.length - 1 ? prev + 1 : prev));
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setItinerary(null);
    setActiveTab("overview");

    const payload = {
      ...form,
      budget: parseFloat(form.budget),
      travelers: parseInt(form.travelers, 10),
      interests: form.interests
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };

    try {
      const res = await fetch(`${API_BASE}/api/plan-trip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed with status ${res.status}`);
      }
      const data = await res.json();
      setItinerary(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-950/30 via-slate-950 to-slate-950">
      {/* Premium Header */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                TravelMate <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">AI</span>
              </h1>
              <p className="text-[10px] text-indigo-400 font-mono tracking-wider uppercase">LangGraph Multi-Agent Engine v1.0</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>Mock Sandbox Active</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 md:px-6 md:py-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Sidebar Form */}
        <section className="lg:col-span-4 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 shadow-2xl shadow-slate-950/80 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white mb-1">Set Your Destination</h2>
            <p className="text-sm text-slate-400">Configure parameters for our AI orchestrator to design your itinerary.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Origin (IATA)"
                name="origin"
                value={form.origin}
                onChange={handleChange}
                placeholder="JFK"
                required
                icon={
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                }
              />
              <Input
                label="Destination"
                name="destination"
                value={form.destination}
                onChange={handleChange}
                placeholder="Tokyo"
                required
                icon={
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Departure"
                name="start_date"
                type="date"
                value={form.start_date}
                onChange={handleChange}
                required
              />
              <Input
                label="Return"
                name="end_date"
                type="date"
                value={form.end_date}
                onChange={handleChange}
                min={form.start_date}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Budget (USD)"
                name="budget"
                type="number"
                value={form.budget}
                onChange={handleChange}
                placeholder="2500"
                required
                icon={
                  <span className="text-sm font-semibold text-slate-500">$</span>
                }
              />
              <Input
                label="Travelers"
                name="travelers"
                type="number"
                min="1"
                value={form.travelers}
                onChange={handleChange}
                required
                icon={
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                }
              />
            </div>

            <Input
              label="Interests (comma separated)"
              name="interests"
              value={form.interests}
              onChange={handleChange}
              placeholder="food, temples, shopping, museum"
              icon={
                <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              }
            />

            <button
              type="submit"
              disabled={loading}
              className="w-full relative group overflow-hidden bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white rounded-2xl py-3.5 px-4 font-semibold text-sm hover:opacity-95 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/20 active:scale-[0.98]"
            >
              <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
              <span className="relative flex items-center justify-center gap-2">
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Executing Agents...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 text-white transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Plan Trip Now
                  </>
                )}
              </span>
            </button>
          </form>

          {error && (
            <div className="bg-red-950/40 border border-red-900 text-red-300 rounded-2xl p-4 flex gap-3 text-sm">
              <svg className="w-5 h-5 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p className="font-semibold text-white">System Error Occurred</p>
                <p className="text-red-400/90 text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}
        </section>

        {/* Right Side: Results & Pipelines */}
        <section className="lg:col-span-8 w-full min-h-[500px]">
          {loading ? (
            /* Premium Agent Progress Pipeline Monitor */
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl flex flex-col justify-center items-center h-full">
              <div className="w-full max-w-lg">
                <div className="text-center mb-8">
                  <div className="inline-block relative">
                    <span className="absolute inset-0 rounded-full bg-indigo-500/20 blur-xl animate-pulse"></span>
                    <div className="h-16 w-16 rounded-2xl bg-slate-900 border border-indigo-500/40 flex items-center justify-center shadow-2xl mb-4 relative z-10 mx-auto">
                      <svg className="w-8 h-8 text-indigo-400 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-15" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                        <path className="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-white">LangGraph Pipeline Orchestration</h3>
                  <p className="text-sm text-slate-400 mt-1">Routing your request through specialized backend LLM agents.</p>
                </div>

                <div className="space-y-4">
                  {AGENT_STEPS.map((step, idx) => {
                    const isActive = idx === activeStep;
                    const isCompleted = idx < activeStep;
                    return (
                      <div
                        key={idx}
                        className={`flex items-center justify-between p-4 rounded-2xl border transition-all duration-300 ${
                          isActive
                            ? "bg-indigo-950/20 border-indigo-500/50 shadow-md shadow-indigo-950/30 translate-x-1"
                            : isCompleted
                            ? "bg-slate-900/60 border-slate-800/80 opacity-80"
                            : "bg-slate-900/20 border-slate-950/40 opacity-40"
                        }`}
                      >
                        <div className="flex items-center gap-3.5">
                          <span className="text-2xl">{step.icon}</span>
                          <div>
                            <p className={`text-sm font-semibold ${isActive ? "text-indigo-300" : "text-white"}`}>
                              {step.name}
                            </p>
                            {isActive && <p className="text-xs text-indigo-400/90 animate-pulse mt-0.5">{step.desc}</p>}
                          </div>
                        </div>
                        <div>
                          {isCompleted ? (
                            <div className="h-6 w-6 rounded-full bg-emerald-500/20 border border-emerald-500 flex items-center justify-center">
                              <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          ) : isActive ? (
                            <div className="h-6 w-6 flex items-center justify-center">
                              <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                              </span>
                            </div>
                          ) : (
                            <div className="h-6 w-6 rounded-full bg-slate-800 border border-slate-700"></div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : itinerary ? (
            /* Results Panel */
            <div className="space-y-6">
              {/* Destination Hero Banner Card */}
              <div className="relative h-48 rounded-3xl overflow-hidden border border-slate-800 shadow-xl group">
                <img
                  src="/travelmate_banner.png"
                  alt="Destination illustration"
                  className="w-full h-full object-cover brightness-[0.4] group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent"></div>
                <div className="absolute bottom-6 left-6 right-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
                  <div>
                    <span className="px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 font-mono text-xs uppercase tracking-wider">
                      Trip Planned Successfully
                    </span>
                    <h2 className="text-3xl font-extrabold text-white mt-2 tracking-tight">
                      Explore {itinerary.trip_request.destination}
                    </h2>
                    <p className="text-slate-300 text-sm mt-1 flex items-center gap-1.5">
                      <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {itinerary.trip_request.start_date} to {itinerary.trip_request.end_date} · {itinerary.days.length} Days
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {itinerary.trip_request.interests.map((interest, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-0.5 rounded-lg bg-slate-900/80 border border-slate-700 text-slate-300 text-xs font-medium capitalize"
                      >
                        #{interest}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Warnings Banner */}
              {itinerary.warnings?.length > 0 && (
                <div className="bg-amber-950/30 border border-amber-900/60 text-amber-300 rounded-2xl p-4 flex gap-3 text-sm">
                  <svg className="w-5 h-5 text-amber-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 className="font-semibold text-white">Orchestrator Alerts</h4>
                    <ul className="list-disc list-inside text-xs text-amber-400/90 space-y-0.5 mt-1">
                      {itinerary.warnings.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Tab Selector */}
              <div className="flex p-1.5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <TabButton active={activeTab === "overview"} onClick={() => setActiveTab("overview")} label="Overview" icon="📊" />
                <TabButton active={activeTab === "flights"} onClick={() => setActiveTab("flights")} label="Flights" icon="✈️" />
                <TabButton active={activeTab === "hotel"} onClick={() => setActiveTab("hotel")} label="Accommodation" icon="🏨" />
                <TabButton active={activeTab === "itinerary"} onClick={() => setActiveTab("itinerary")} label="Itinerary" icon="📅" />
              </div>

              {/* Dynamic Tab Content */}
              <div className="transition-all duration-300">
                {activeTab === "overview" && (
                  <div className="space-y-6">
                    {/* Budget Summary Card */}
                    {itinerary.budget_summary && (
                      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-lg font-bold text-white">Financial Audit</h3>
                            <p className="text-xs text-slate-400">Total spending projection compared against budget cap.</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold font-mono ${
                            itinerary.budget_summary.over_budget
                              ? "bg-red-500/10 border border-red-500/30 text-red-400"
                              : "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
                          }`}>
                            {itinerary.budget_summary.over_budget ? "⚠️ Budget Overdraft" : "✓ Within Budget"}
                          </span>
                        </div>

                        {/* Progress Bar visualizer */}
                        <div className="space-y-2">
                          <div className="h-4 w-full bg-slate-950 rounded-full overflow-hidden flex border border-slate-850">
                            <ProgressBarSegment value={itinerary.budget_summary.flights_cost} total={itinerary.budget_summary.total_budget} color="bg-cyan-500" />
                            <ProgressBarSegment value={itinerary.budget_summary.hotel_cost} total={itinerary.budget_summary.total_budget} color="bg-purple-500" />
                            <ProgressBarSegment value={itinerary.budget_summary.activities_cost} total={itinerary.budget_summary.total_budget} color="bg-emerald-500" />
                            <ProgressBarSegment value={itinerary.budget_summary.food_cost} total={itinerary.budget_summary.total_budget} color="bg-amber-500" />
                          </div>
                          <div className="flex flex-wrap gap-4 text-xs font-mono text-slate-400">
                            <LegendItem color="bg-cyan-500" label="Flights" value={itinerary.budget_summary.flights_cost} />
                            <LegendItem color="bg-purple-500" label="Hotel" value={itinerary.budget_summary.hotel_cost} />
                            <LegendItem color="bg-emerald-500" label="Activities" value={itinerary.budget_summary.activities_cost} />
                            <LegendItem color="bg-amber-500" label="Food" value={itinerary.budget_summary.food_cost} />
                          </div>
                        </div>

                        {/* Detailed Grid of Financial Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-800/80">
                          <MetricBox label="Allocated Cap" value={`$${itinerary.budget_summary.total_budget.toLocaleString()}`} />
                          <MetricBox
                            label="Projected Spend"
                            value={`$${(
                              itinerary.budget_summary.flights_cost +
                              itinerary.budget_summary.hotel_cost +
                              itinerary.budget_summary.activities_cost +
                              itinerary.budget_summary.food_cost
                            ).toLocaleString()}`}
                          />
                          <MetricBox
                            label="Remaining Fund"
                            value={`$${itinerary.budget_summary.remaining.toLocaleString()}`}
                            status={itinerary.budget_summary.over_budget ? "error" : "success"}
                          />
                          <MetricBox
                            label="Day Average"
                            value={`$${(
                              (itinerary.budget_summary.hotel_cost +
                                itinerary.budget_summary.activities_cost +
                                itinerary.budget_summary.food_cost) /
                              itinerary.days.length
                            ).toFixed(0)}/day`}
                          />
                        </div>
                      </div>
                    )}

                    {/* Summary Quick Preview Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-5 space-y-4">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">✈️</span>
                          <h4 className="font-bold text-white">Optimal Flight Option</h4>
                        </div>
                        {itinerary.flights?.length > 0 ? (
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-semibold text-white">{itinerary.flights[0].airline} Airline</p>
                              <span className="font-mono text-sm font-bold text-cyan-400">${itinerary.flights[0].price.toFixed(2)}</span>
                            </div>
                            <div className="flex text-xs text-slate-400 gap-4">
                              <span>⏱ {itinerary.flights[0].duration}</span>
                              <span>• {itinerary.flights[0].stops} Stop(s)</span>
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500">No flight alternatives listed.</p>
                        )}
                      </div>

                      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-5 space-y-4">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">🏨</span>
                          <h4 className="font-bold text-white">Hotel Selection</h4>
                        </div>
                        {itinerary.hotel ? (
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-semibold text-white truncate max-w-[200px]">{itinerary.hotel.name}</p>
                              <span className="font-mono text-sm font-bold text-purple-400">${itinerary.hotel.price_per_night.toFixed(2)}/night</span>
                            </div>
                            <p className="text-xs text-slate-400 line-clamp-1">📍 {itinerary.hotel.address}</p>
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500">No hotel accommodation selected.</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "flights" && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <span>✈️</span> Flight Search Offers
                      </h3>
                      <span className="text-xs font-mono text-slate-400">{itinerary.flights?.length || 0} Options Found</span>
                    </div>

                    <div className="space-y-4">
                      {itinerary.flights?.map((flight, idx) => (
                        <div
                          key={idx}
                          className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition duration-300 flex flex-col md:flex-row md:items-center justify-between gap-6"
                        >
                          <div className="flex items-center gap-4">
                            <div className="h-12 w-12 rounded-xl bg-slate-800 border border-slate-750 flex items-center justify-center font-bold text-slate-300">
                              {flight.airline.slice(0, 2)}
                            </div>
                            <div>
                              <h4 className="font-bold text-white">{flight.airline}</h4>
                              <p className="text-xs text-slate-400 font-mono mt-0.5">Duration: {flight.duration}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-8 justify-between md:justify-end">
                            <div className="text-left md:text-right font-mono">
                              <p className="text-xs text-slate-500">Stops</p>
                              <p className={`text-sm font-semibold ${flight.stops === 0 ? "text-emerald-400" : "text-slate-300"}`}>
                                {flight.stops === 0 ? "Non-stop" : `${flight.stops} Stop(s)`}
                              </p>
                            </div>

                            <div className="text-right">
                              <p className="text-2xl font-bold font-mono text-cyan-400">${flight.price.toFixed(0)}</p>
                              <button className="text-xs text-indigo-400 font-semibold hover:text-indigo-300 underline mt-0.5 block">
                                Book Flight
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === "hotel" && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <span>🏨</span> Recommended Stay
                    </h3>

                    {itinerary.hotel ? (
                      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div>
                            <h4 className="text-2xl font-extrabold text-white tracking-tight">{itinerary.hotel.name}</h4>
                            <p className="text-sm text-slate-400 flex items-center gap-1.5 mt-1.5">
                              <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              {itinerary.hotel.address}
                            </p>
                          </div>
                          <div className="text-left md:text-right font-mono">
                            <span className="text-xs text-slate-500 block">Nightly Rate</span>
                            <span className="text-2xl font-extrabold text-purple-400">${itinerary.hotel.price_per_night.toFixed(0)}</span>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 border-t border-slate-800/80 pt-6">
                          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-4">
                            <span className="text-xs text-slate-500 block">Guest Rating</span>
                            <span className="text-lg font-bold text-white flex items-center gap-1.5 mt-1">
                              ⭐ {itinerary.hotel.rating ? itinerary.hotel.rating.toFixed(1) : "N/A"} / 5.0
                            </span>
                          </div>
                          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-4">
                            <span className="text-xs text-slate-500 block">Status Selection</span>
                            <span className="text-lg font-bold text-emerald-400 mt-1 block">✓ Reserved Mock</span>
                          </div>
                        </div>

                        <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold py-3 px-4 rounded-xl transition">
                          Book Accommodation
                        </button>
                      </div>
                    ) : (
                      <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-8 text-center text-slate-500">
                        No accommodation is configured matching the budget.
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "itinerary" && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <span>📅</span> Day-by-Day Schedule
                    </h3>

                    <div className="space-y-6">
                      {itinerary.days?.map((day) => (
                        <div key={day.day_number} className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 space-y-4">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/60 pb-3 gap-2">
                            <div>
                              <h4 className="text-lg font-bold text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-indigo-500"></span>
                                Day {day.day_number}
                              </h4>
                              <p className="text-xs text-slate-400 font-mono mt-0.5">{day.date}</p>
                            </div>
                            <div className="text-left sm:text-right font-mono">
                              <span className="text-xs text-slate-500">Daily Projection:</span>
                              <span className="text-sm font-bold text-emerald-400 ml-1.5">${day.estimated_day_cost.toFixed(2)}</span>
                            </div>
                          </div>

                          {/* Activities */}
                          <div className="space-y-3">
                            <h5 className="text-xs font-mono text-slate-500 uppercase tracking-widest">Plan & Activities</h5>
                            {day.activities?.length > 0 ? (
                              <div className="space-y-3">
                                {day.activities.map((act, i) => (
                                  <div key={i} className="bg-slate-950/40 border border-slate-800/60 rounded-2xl p-4 space-y-2 hover:border-slate-700/80 transition duration-300">
                                    <div className="flex items-start justify-between gap-4">
                                      <div>
                                        <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] font-mono text-indigo-400 uppercase tracking-wider capitalize">
                                          {act.category}
                                        </span>
                                        <h6 className="font-bold text-white text-sm mt-1.5">{act.name}</h6>
                                      </div>
                                      <span className="font-mono text-xs font-bold text-indigo-300 shrink-0">
                                        {act.estimated_cost > 0 ? `$${act.estimated_cost.toFixed(0)}` : "Free"}
                                      </span>
                                    </div>
                                    <p className="text-xs text-slate-400 leading-relaxed font-sans">{act.notes}</p>
                                    <p className="text-[10px] text-slate-500 flex items-center gap-1 font-mono">
                                      ⏱ Duration: {act.duration_hours} hr
                                    </p>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-sm text-slate-500 italic">No scheduled attractions. Day open for wandering.</p>
                            )}
                          </div>

                          {/* Meals */}
                          {day.meals?.length > 0 && (
                            <div className="space-y-2 pt-2">
                              <h5 className="text-xs font-mono text-slate-500 uppercase tracking-widest">Culinary Suggestions</h5>
                              <div className="flex flex-wrap gap-2">
                                {day.meals.map((meal, idx) => (
                                  <span key={idx} className="px-3 py-1 rounded-full bg-slate-950/60 border border-slate-850 text-xs text-slate-300">
                                    🍴 {meal}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* Intro / Call to Action Card */
            <div className="bg-slate-900/20 border border-dashed border-slate-850 rounded-3xl p-8 flex flex-col justify-center items-center h-full text-center">
              <div className="max-w-md space-y-4">
                <div className="h-16 w-16 bg-slate-900/60 border border-slate-800 rounded-2xl flex items-center justify-center text-3xl shadow-xl mx-auto mb-2 animate-bounce">
                  🏝️
                </div>
                <h3 className="text-lg font-bold text-white">No Active Itinerary</h3>
                <p className="text-sm text-slate-400">
                  Submit the planner form with your travel details to configure flights, accommodations, and an organized day-by-day plan.
                </p>
                <div className="relative rounded-2xl overflow-hidden border border-slate-800/80 shadow-2xl h-40 max-w-xs mx-auto">
                  <img
                    src="/travelmate_banner.png"
                    alt="Travel banner representation"
                    className="w-full h-full object-cover opacity-60"
                  />
                  <div className="absolute inset-0 bg-slate-950/20"></div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

// UI helper components
function Input({ label, icon, ...props }) {
  return (
    <label className="flex flex-col text-xs font-bold text-slate-400 gap-1.5 w-full">
      {label}
      <div className="relative flex items-center">
        {icon && <div className="absolute left-3.5 z-10">{icon}</div>}
        <input
          {...props}
          className={`w-full bg-slate-950 border border-slate-850 text-slate-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition placeholder-slate-600 ${
            icon ? "pl-10" : ""
          }`}
        />
      </div>
    </label>
  );
}

function TabButton({ active, onClick, label, icon }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-semibold tracking-wide transition duration-200 ${
        active
          ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
          : "text-slate-400 hover:bg-slate-950/60 hover:text-white"
      }`}
    >
      <span>{icon}</span>
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}

function ProgressBarSegment({ value, total, color }) {
  const percent = Math.min((value / total) * 100, 100);
  if (percent <= 0) return null;
  return <div style={{ width: `${percent}%` }} className={`h-full ${color} transition-all duration-500`} />;
}

function LegendItem({ color, label, value }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`}></span>
      <span>
        {label}: <span className="text-slate-200 font-bold">${value.toFixed(0)}</span>
      </span>
    </div>
  );
}

function MetricBox({ label, value, status }) {
  return (
    <div className="bg-slate-950/40 border border-slate-800/80 rounded-2xl p-4">
      <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">{label}</span>
      <span
        className={`text-base font-extrabold mt-1 block tracking-tight ${
          status === "success" ? "text-emerald-400" : status === "error" ? "text-red-400" : "text-white"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

