import React, { useState } from 'react';
import { Activity, Lock, Mail, ArrowLeft, CheckCircle2, Shield, AlertCircle, UserCheck } from 'lucide-react';

export default function LoginView({ onLoginSuccess, onBackToWelcome }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const DEMO_PROFILES = [
    {
      id: 'ASTRO-001',
      name: 'Dr. Sarah Chen',
      role: 'Chief Medical Officer / Flight Surgeon',
      email: 'sarah.chen@starhealers.space',
      callsign: 'MED-SURGEON-01',
    },
    {
      id: 'ASTRO-002',
      name: 'Marcus Vance',
      role: 'Flight Engineer & Systems Specialist',
      email: 'marcus.vance@starhealers.space',
      callsign: 'FLIGHT-ENG-02',
    },
    {
      id: 'ASTRO-003',
      name: 'Dr. Elena Rostova',
      role: 'Payload & Health Specialist',
      email: 'elena.rostova@starhealers.space',
      callsign: 'BIO-SPEC-03',
    },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Please enter your Medical ID or Email.');
      return;
    }
    if (!password.trim()) {
      setError('Please enter your Security Access Key.');
      return;
    }
    if (password.length < 4) {
      setError('Security Access Key must be at least 4 characters.');
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLoginSuccess({
        name: email.includes('@') ? email.split('@')[0].replace('.', ' ').toUpperCase() : email,
        role: 'Authorized Medical Officer',
        email: email,
        callsign: 'MED-ACTIVE',
      });
    }, 600);
  };

  const handleSelectDemo = (profile) => {
    setEmail(profile.email);
    setPassword('••••••••');
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLoginSuccess(profile);
    }, 400);
  };

  return (
    <div className="relative min-h-screen bg-[#060913] text-[#F8FAFC] flex flex-col justify-center items-center px-4 py-8 overflow-hidden selection:bg-cyan-500 selection:text-black">
      {/* Background Ambience */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 right-10 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.05)_1px,transparent_1px)] [background-size:24px_24px] opacity-40" />
      </div>

      {/* Main Login Card */}
      <div className="relative z-10 w-full max-w-md">
        {/* Back Link */}
        <button
          onClick={onBackToWelcome}
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors mb-6 group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>Back to Welcome Page</span>
        </button>

        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          {/* Brand Header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/40 shadow-lg shadow-cyan-500/10 mb-3">
              <Activity className="w-6 h-6 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              Medical Officer Access
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Sign in to monitor astronaut telemetry and clinical triage
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-950/50 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Medical Officer ID or Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. sarah.chen@starhealers.space"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Security Access Key
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter security key"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/20 transition-all duration-200 disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? 'Verifying Credentials...' : 'Sign In to StarHealers'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800" />
            </div>
            <div className="relative flex justify-center text-[11px] uppercase">
              <span className="bg-slate-900 px-3 text-slate-500 font-mono">
                Or Instant Demo Access
              </span>
            </div>
          </div>

          {/* Quick Demo Profiles */}
          <div className="space-y-2">
            <div className="text-[11px] font-medium text-slate-400 mb-1">
              Select a pre-authorized flight profile:
            </div>
            {DEMO_PROFILES.map((profile) => (
              <button
                key={profile.id}
                onClick={() => handleSelectDemo(profile)}
                className="w-full flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-cyan-500/40 text-left transition-all group"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 font-bold text-xs flex items-center justify-center border border-cyan-500/30">
                    {profile.name[0]}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors">
                      {profile.name}
                    </div>
                    <div className="text-[10px] text-slate-400">{profile.role}</div>
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
              </button>
            ))}
          </div>

          {/* Security Notice */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-start gap-2 text-[11px] text-slate-400">
            <Shield className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              Simulated clinical operational environment. Demonstrates authenticated medical officer monitoring for space missions.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
