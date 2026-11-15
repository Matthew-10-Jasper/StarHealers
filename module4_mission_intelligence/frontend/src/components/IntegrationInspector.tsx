import React, { useState } from 'react';
import { Share2, Check, Copy, ExternalLink, Send, ShieldCheck, Layers } from 'lucide-react';
import { api } from '../services/api';

export const IntegrationInspector: React.FC = () => {
  const [contractJson, setContractJson] = useState<string | null>(null);
  const [deliveryResult, setDeliveryResult] = useState<any | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>('MODULE_1_ASTRONAUT_HEALTH_MONITORING');
  const [isCopied, setIsCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchContract = async () => {
    try {
      setIsLoading(true);
      const data = await api.getIntegrationContract();
      setContractJson(JSON.stringify(data, null, 2));
    } catch (e: any) {
      alert('Failed to fetch integration contract: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const deliverMock = async () => {
    try {
      setIsLoading(true);
      const res = await api.deliverMockIntegration(selectedModule);
      setDeliveryResult(res);
    } catch (e: any) {
      alert('Mock delivery failed: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (contractJson) {
      navigator.clipboard.writeText(contractJson);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#1E293B] gap-2">
        <div className="flex items-center space-x-2">
          <Share2 className="h-5 w-5 text-cyan-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Future Teammate Integration Inspector & Mock Adapters
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchContract}
            disabled={isLoading}
            className="px-3 py-1 rounded text-xs font-mono font-bold bg-cyan-950/60 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-900/60 transition"
          >
            Inspect Active Contract JSON
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-4 text-xs font-mono">
        {/* Left: Mock Dispatcher */}
        <div className="lg:col-span-5 bg-[#060913] p-4 rounded-lg border border-[#1E293B] flex flex-col justify-between">
          <div>
            <span className="text-slate-400 font-bold uppercase tracking-wider block mb-2">
              Dispatch Context To Downstream Module
            </span>
            <p className="text-[11px] text-slate-500 font-sans leading-relaxed mb-3">
              Modules 1–3 are built independently by teammates. Module 4 emits a verified, versioned
              contract through pluggable abstract adapters without depending on their source code.
            </p>

            <label className="block text-[11px] text-slate-400 mb-1">TARGET ADAPTER</label>
            <select
              value={selectedModule}
              onChange={(e) => setSelectedModule(e.target.value)}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded px-3 py-1.5 text-slate-200 text-xs mb-3 focus:outline-none focus:border-cyan-500"
            >
              <option value="MODULE_1_ASTRONAUT_HEALTH_MONITORING">Module 1: Astronaut Health Monitoring</option>
              <option value="MODULE_3_CLINICAL_TRIAGE_ENGINE">Module 3: Clinical Triage Engine</option>
              <option value="MODULE_5_RADIATION_CO2_SLEEP_SIMULATOR">Module 5: Radiation & Sleep Simulator</option>
            </select>

            <button
              onClick={deliverMock}
              disabled={isLoading}
              className="w-full py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold transition flex items-center justify-center space-x-2"
            >
              <Send className="h-3.5 w-3.5" />
              <span>TEST ADAPTER DISPATCH</span>
            </button>
          </div>

          {deliveryResult && (
            <div className="mt-4 p-3 rounded bg-slate-900 border border-cyan-500/30 text-[11px]">
              <span className="text-cyan-400 font-bold block mb-1">MOCK ADAPTER ACKNOWLEDGEMENT:</span>
              <pre className="text-slate-300 overflow-x-auto text-[10px]">
                {JSON.stringify(deliveryResult, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Right: Live JSON Contract Viewer */}
        <div className="lg:col-span-7 bg-[#060913] p-4 rounded-lg border border-[#1E293B]">
          <div className="flex items-center justify-between pb-2 border-b border-[#1E293B] mb-2">
            <span className="text-slate-400 uppercase text-[10px] tracking-wider">
              STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT (v1.0.0)
            </span>
            {contractJson && (
              <button
                onClick={handleCopy}
                className="flex items-center space-x-1 text-[11px] text-cyan-400 hover:text-cyan-300"
              >
                {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{isCopied ? 'Copied' : 'Copy'}</span>
              </button>
            )}
          </div>

          <div className="max-h-64 overflow-y-auto text-[11px] text-slate-300">
            {contractJson ? (
              <pre className="text-slate-300 font-mono text-[10px] whitespace-pre-wrap">
                {contractJson}
              </pre>
            ) : (
              <div className="py-12 text-center text-slate-600">
                Click &quot;Inspect Active Contract JSON&quot; above to view live payload.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

