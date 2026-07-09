"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Key, 
  Lock, 
  Terminal, 
  Activity, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Save, 
  Database,
  Shield,
  Eye,
  EyeOff,
  Cpu,
  Settings2
} from "lucide-react";

interface LogEntry {
  id: string;
  timestamp: string;
  question_length: number;
  response_length: number;
  response_time_ms: number;
  status_code: number;
}

interface StatsData {
  total_requests: number;
  requests_today: number;
  requests_last_minute: number;
  avg_response_time_ms: number;
  success_rate: number;
  logs: LogEntry[];
  rpm_limit: number;
}

export default function AdminPortal() {
  const [password, setPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [stats, setStats] = useState<StatsData | null>(null);
  
  // Configurations
  const [activeProvider, setActiveProvider] = useState("gemini");
  const [activeModel, setActiveModel] = useState("gemini-2.5-flash");
  const [geminiKey, setGeminiKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [openrouterKey, setOpenrouterKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [newPasswordInput, setNewPasswordInput] = useState("");
  
  // UI visibility states
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({
    gemini: false,
    openai: false,
    openrouter: false,
    anthropic: false,
  });
  
  const [saveStatus, setSaveStatus] = useState({ success: false, message: "" });
  const [loading, setLoading] = useState(false);
  const refreshTimer = useRef<NodeJS.Timeout | null>(null);

  const toggleKeyVisibility = (provider: string) => {
    setShowKeys((prev) => ({ ...prev, [provider]: !prev[provider] }));
  };

  // Check for saved password on mount
  useEffect(() => {
    const savedPassword = localStorage.getItem("examai_admin_password");
    if (savedPassword) {
      setPassword(savedPassword);
      verifyPassword(savedPassword);
    }
  }, []);

  // Set up auto-refresh when logged in
  useEffect(() => {
    if (isLoggedIn) {
      fetchStats();
      refreshTimer.current = setInterval(fetchStats, 10000); // refresh every 10s
    }
    return () => {
      if (refreshTimer.current) clearInterval(refreshTimer.current);
    };
  }, [isLoggedIn]);

  const verifyPassword = async (passToVerify: string) => {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/config", {
        headers: {
          Authorization: `Bearer ${passToVerify}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setActiveProvider(data.provider);
        setActiveModel(data.model);
        setGeminiKey(data.gemini_api_key);
        setOpenaiKey(data.openai_api_key);
        setOpenrouterKey(data.openrouter_api_key);
        setAnthropicKey(data.anthropic_api_key);
        setIsLoggedIn(true);
        localStorage.setItem("examai_admin_password", passToVerify);
        setLoginError("");
      } else {
        setLoginError("Invalid admin credentials.");
        localStorage.removeItem("examai_admin_password");
      }
    } catch (err) {
      setLoginError("Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.trim()) {
      verifyPassword(password);
    }
  };

  const fetchStats = async () => {
    try {
      const currentPassword = localStorage.getItem("examai_admin_password") || password;
      const res = await fetch("/api/admin/stats", {
        headers: {
          Authorization: `Bearer ${currentPassword}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error("Error fetching stats:", err);
    }
  };

  const handleUpdateConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveStatus({ success: false, message: "" });
    const currentPassword = localStorage.getItem("examai_admin_password") || password;

    try {
      const payload: Record<string, string> = {
        provider: activeProvider,
        model: activeModel,
        gemini_api_key: geminiKey,
        openai_api_key: openaiKey,
        openrouter_api_key: openrouterKey,
        anthropic_api_key: anthropicKey,
      };
      
      if (newPasswordInput.trim() !== "") {
        payload.admin_password = newPasswordInput;
      }

      const res = await fetch("/api/admin/config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${currentPassword}`,
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setSaveStatus({ success: true, message: "System settings updated successfully!" });
        if (newPasswordInput.trim() !== "") {
          localStorage.setItem("examai_admin_password", newPasswordInput);
          setPassword(newPasswordInput);
          setNewPasswordInput("");
        }
        fetchStats();
      } else {
        const data = await res.json();
        setSaveStatus({ success: false, message: data.error || "Update failed." });
      }
    } catch (err) {
      setSaveStatus({ success: false, message: "Connection error." });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("examai_admin_password");
    setIsLoggedIn(false);
    setStats(null);
    setPassword("");
  };

  // Helper to suggest standard model name based on provider
  const handleProviderChange = (newProvider: string) => {
    setActiveProvider(newProvider);
    if (newProvider === "gemini") {
      setActiveModel("gemini-2.5-flash");
    } else if (newProvider === "openai") {
      setActiveModel("gpt-4o-mini");
    } else if (newProvider === "openrouter") {
      setActiveModel("google/gemini-2.5-flash");
    } else if (newProvider === "anthropic") {
      setActiveModel("claude-3-5-sonnet-20241022");
    }
  };

  if (!isLoggedIn) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4 bg-[#0a0512] text-[#e0e0fa] relative overflow-hidden font-mono">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#140d25_1px,transparent_1px),linear-gradient(to_bottom,#140d25_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-60"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#bc39e1] rounded-full filter blur-[150px] opacity-10 animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#00f3ff] rounded-full filter blur-[150px] opacity-10 animate-pulse"></div>

        <div className="relative w-full max-w-md p-8 rounded-lg bg-[#0e0a1f]/90 border border-[#c135e3]/30 shadow-[0_0_30px_rgba(193,53,227,0.15)] backdrop-blur-md">
          <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[size:100%_4px]"></div>
          
          <div className="text-center mb-8">
            <div className="inline-flex p-3 rounded-full bg-[#c135e3]/10 border border-[#c135e3]/40 mb-4 shadow-[0_0_15px_rgba(193,53,227,0.2)]">
              <Terminal className="w-8 h-8 text-[#00f3ff] animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-[#00f3ff] via-[#d946ef] to-[#c135e3] drop-shadow-[0_0_10px_rgba(193,53,227,0.3)]">
              EXAMAI PORTAL
            </h1>
            <p className="text-xs text-[#a09bb5] mt-2 tracking-wider">
              CENTRAL ADMIN GATEWAY v2.0 (MULTI-LLM)
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs uppercase text-[#00f3ff] tracking-widest flex items-center gap-2">
                <Lock className="w-3 h-3" /> Admin Key
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="ENTER ACCESS PHRASE..."
                disabled={loading}
                className="w-full px-4 py-3 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] placeholder-[#5d5875] focus:outline-none focus:border-[#00f3ff] transition-all font-mono text-sm"
              />
            </div>

            {loginError && (
              <div className="text-xs text-red-400 bg-red-950/30 border border-red-500/30 p-3 rounded flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !password}
              className="relative w-full py-3 bg-gradient-to-r from-[#c135e3] to-[#00f3ff] text-[#07040e] font-bold rounded uppercase tracking-widest transition-all hover:scale-[1.01] disabled:opacity-50 active:scale-[0.98]"
            >
              {loading ? "Decrypting..." : "Access System"}
            </button>
          </form>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6 md:p-8 bg-[#0a0512] text-[#e0e0fa] font-mono relative overflow-x-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#140d25_1px,transparent_1px),linear-gradient(to_bottom,#140d25_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40"></div>
      <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-[#c135e3] rounded-full filter blur-[180px] opacity-[0.07]"></div>
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.15)_50%)] bg-[size:100%_4px]"></div>

      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Terminal className="w-8 h-8 text-[#00f3ff]" />
            <div>
              <h1 className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-[#00f3ff] via-[#d946ef] to-[#c135e3] drop-shadow-[0_0_5px_rgba(0,243,255,0.2)]">
                EXAMAI ADMIN PANEL
              </h1>
              <p className="text-xs text-[#a09bb5] mt-0.5 tracking-widest">
                ACTIVE PROVIDER: <span className="text-[#00f3ff] uppercase font-bold">{activeProvider}</span> ({activeModel})
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={fetchStats}
              className="px-4 py-2 border border-[#00f3ff]/30 text-[#00f3ff] hover:bg-[#00f3ff]/10 rounded text-xs uppercase tracking-widest flex items-center gap-2 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-[#c135e3]/30 text-[#c135e3] hover:bg-[#c135e3]/10 rounded text-xs uppercase tracking-widest transition-all"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Dashboard Cards Grid */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md flex flex-col justify-between min-h-[140px]">
            <div className="flex justify-between items-start">
              <p className="text-xs uppercase text-[#a09bb5] tracking-widest">Queries Today</p>
              <Activity className="w-5 h-5 text-[#00f3ff]" />
            </div>
            <h2 className="text-3xl font-bold text-[#e0e0fa] my-4">
              {stats ? stats.requests_today : "..."}
            </h2>
            <p className="text-[10px] text-[#a09bb5]">Cumulative queries today (UTC)</p>
          </div>

          <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md flex flex-col justify-between min-h-[140px]">
            <div className="flex justify-between items-start">
              <p className="text-xs uppercase text-[#a09bb5] tracking-widest">Current RPM Load</p>
              <Cpu className="w-5 h-5 text-[#d946ef]" />
            </div>
            <h2 className="text-3xl font-bold text-[#e0e0fa] my-4">
              {stats ? `${stats.requests_last_minute} / ${stats.rpm_limit}` : "..."}
            </h2>
            <p className="text-[10px] text-[#a09bb5]">Queries in the last 60 seconds</p>
          </div>

          <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md flex flex-col justify-between min-h-[140px]">
            <div className="flex justify-between items-start">
              <p className="text-xs uppercase text-[#a09bb5] tracking-widest">Avg Response Time</p>
              <Clock className="w-5 h-5 text-[#eab308]" />
            </div>
            <h2 className="text-3xl font-bold text-[#e0e0fa] my-4">
              {stats ? `${stats.avg_response_time_ms} ms` : "..."}
            </h2>
            <p className="text-[10px] text-[#a09bb5]">Average processing latency</p>
          </div>

          <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md flex flex-col justify-between min-h-[140px]">
            <div className="flex justify-between items-start">
              <p className="text-xs uppercase text-[#a09bb5] tracking-widest">System Success Rate</p>
              <CheckCircle className="w-5 h-5 text-[#22c55e]" />
            </div>
            <h2 className="text-3xl font-bold text-[#e0e0fa] my-4">
              {stats ? `${stats.success_rate}%` : "..."}
            </h2>
            <p className="text-[10px] text-[#a09bb5]">Based on last 15 queries</p>
          </div>
        </section>

        {/* Configurations & Stats Main Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Settings Column */}
          <div className="lg:col-span-1 space-y-6">
            <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md">
              <h2 className="text-sm font-bold uppercase text-[#00f3ff] tracking-widest flex items-center gap-2 mb-6">
                <Settings2 className="w-4 h-4" /> Provider Settings
              </h2>

              <form onSubmit={handleUpdateConfig} className="space-y-4">
                
                {/* Provider Selector */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    Active AI Provider
                  </label>
                  <select
                    value={activeProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="w-full px-3 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                  >
                    <option value="gemini">Google Gemini</option>
                    <option value="openrouter">OpenRouter</option>
                    <option value="openai">OpenAI (ChatGPT)</option>
                    <option value="anthropic">Anthropic (Claude)</option>
                  </select>
                </div>

                {/* Model Input */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    Model Name
                  </label>
                  <input
                    type="text"
                    value={activeModel}
                    onChange={(e) => setActiveModel(e.target.value)}
                    placeholder="ENTER MODEL STRING..."
                    className="w-full px-3 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                  />
                </div>

                {/* Gemini API Key */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    Gemini API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.gemini ? "text" : "password"}
                      value={geminiKey}
                      onChange={(e) => setGeminiKey(e.target.value)}
                      placeholder="GEMINI KEY..."
                      className="w-full pl-3 pr-10 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                    />
                    <button
                      type="button"
                      onClick={() => toggleKeyVisibility("gemini")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a09bb5] hover:text-[#e0e0fa]"
                    >
                      {showKeys.gemini ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* OpenRouter API Key */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    OpenRouter API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.openrouter ? "text" : "password"}
                      value={openrouterKey}
                      onChange={(e) => setOpenrouterKey(e.target.value)}
                      placeholder="OPENROUTER KEY..."
                      className="w-full pl-3 pr-10 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                    />
                    <button
                      type="button"
                      onClick={() => toggleKeyVisibility("openrouter")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a09bb5] hover:text-[#e0e0fa]"
                    >
                      {showKeys.openrouter ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* OpenAI API Key */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    OpenAI API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.openai ? "text" : "password"}
                      value={openaiKey}
                      onChange={(e) => setOpenaiKey(e.target.value)}
                      placeholder="OPENAI KEY..."
                      className="w-full pl-3 pr-10 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                    />
                    <button
                      type="button"
                      onClick={() => toggleKeyVisibility("openai")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a09bb5] hover:text-[#e0e0fa]"
                    >
                      {showKeys.openai ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Anthropic API Key */}
                <div className="space-y-1">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    Anthropic API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.anthropic ? "text" : "password"}
                      value={anthropicKey}
                      onChange={(e) => setAnthropicKey(e.target.value)}
                      placeholder="ANTHROPIC KEY..."
                      className="w-full pl-3 pr-10 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                    />
                    <button
                      type="button"
                      onClick={() => toggleKeyVisibility("anthropic")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a09bb5] hover:text-[#e0e0fa]"
                    >
                      {showKeys.anthropic ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Change admin password */}
                <div className="space-y-1 pt-2 border-t border-[#c135e3]/10">
                  <label className="text-[10px] text-[#a09bb5] uppercase tracking-wider block">
                    Change Portal Password
                  </label>
                  <input
                    type="password"
                    value={newPasswordInput}
                    onChange={(e) => setNewPasswordInput(e.target.value)}
                    placeholder="LEAVE BLANK TO KEEP UNCHANGED..."
                    className="w-full px-3 py-2 bg-[#07040e] border border-[#c135e3]/30 rounded text-[#e0e0fa] text-xs font-mono focus:outline-none focus:border-[#00f3ff]"
                  />
                </div>

                {saveStatus.message && (
                  <div className={`text-xs p-3 rounded flex items-center gap-2 border ${
                    saveStatus.success 
                      ? "text-[#22c55e] bg-green-950/20 border-green-500/20" 
                      : "text-red-400 bg-red-950/20 border-red-500/20"
                  }`}>
                    {saveStatus.success ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    <span className="text-[10px]">{saveStatus.message}</span>
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full py-2.5 bg-gradient-to-r from-[#c135e3] to-[#00f3ff] text-[#07040e] font-bold rounded text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
                >
                  <Save className="w-4 h-4" /> Save Settings
                </button>
              </form>
            </div>

            {/* DB Status */}
            <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md space-y-4">
              <h2 className="text-xs font-bold uppercase text-[#00f3ff] tracking-widest flex items-center gap-2">
                <Database className="w-4 h-4" /> DB Storage Status
              </h2>
              <div className="text-[10px] space-y-2.5">
                <div className="flex justify-between border-b border-[#c135e3]/10 pb-2">
                  <span className="text-[#a09bb5]">Host</span>
                  <span className="text-[#e0e0fa] text-[9px] font-mono">db.vrmbzcdjxqckaksxfbiz.supabase.co</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#a09bb5]">Total Logs Recorded</span>
                  <span className="text-[#00f3ff] font-bold">{stats ? stats.total_requests : "..."}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Logs Column */}
          <div className="lg:col-span-2">
            <div className="p-6 rounded-lg bg-[#0e0a1f]/80 border border-[#c135e3]/20 shadow-[0_0_15px_rgba(193,53,227,0.05)] backdrop-blur-md h-full flex flex-col">
              <h2 className="text-md font-bold uppercase text-[#00f3ff] tracking-widest flex items-center gap-2 mb-6">
                <Terminal className="w-4 h-4" /> Live Terminal Logs
              </h2>

              <div className="overflow-x-auto flex-1">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#c135e3]/20 text-[#a09bb5]">
                      <th className="py-3 px-2 font-semibold">Timestamp</th>
                      <th className="py-3 px-2 font-semibold">Prompt Length</th>
                      <th className="py-3 px-2 font-semibold">Response Length</th>
                      <th className="py-3 px-2 font-semibold">Latency</th>
                      <th className="py-3 px-2 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats && stats.logs.length > 0 ? (
                      stats.logs.map((log) => {
                        const isSuccess = log.status_code >= 200 && log.status_code < 300;
                        const dateStr = new Date(log.timestamp).toLocaleTimeString();
                        return (
                          <tr key={log.id} className="border-b border-[#c135e3]/10 hover:bg-[#c135e3]/5 transition-all">
                            <td className="py-3 px-2 text-[#e0e0fa]">{dateStr}</td>
                            <td className="py-3 px-2 text-[#a09bb5]">{log.question_length} chars</td>
                            <td className="py-3 px-2 text-[#a09bb5]">{log.response_length || 0} chars</td>
                            <td className="py-3 px-2 text-[#eab308]">{log.response_time_ms} ms</td>
                            <td className="py-3 px-2">
                              <span className={`inline-block px-2 py-0.5 rounded-[3px] text-[10px] font-bold ${
                                isSuccess 
                                  ? "bg-green-950/30 text-[#22c55e] border border-green-500/20" 
                                  : "bg-red-950/30 text-red-400 border border-red-500/20"
                              }`}>
                                {log.status_code}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={5} className="text-center py-8 text-[#5d5875]">
                          {stats ? "No logs recorded yet." : "Decrypting logs..."}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

        </div>

      </div>
    </main>
  );
}
