/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#060913",
        card: "#0F172A",
        borderInactive: "#1E293B",
        textPrimary: "#F8FAFC",
        // Health Severity Colors
        healthNormal: "#22C55E",
        healthWarning: "#F59E0B",
        healthCritical: "#EF4444",
        healthNoData: "#64748B",
        // Palette 2: Core Vitals & Telemetry (Module 1)
        vitalCyan: "#00F0FF",
        vitalBlue: "#3B82F6",
        // Palette 4: Rule-Based Alert & Triage (Module 3)
        triageCrimson: "#EF4444",
        triageAmber: "#F59E0B",
        // Other Team Palettes for Navigation & Integration
        rppgRose: "#F43F5E",
        rppgCoral: "#FB7185",
        anomalyViolet: "#8B5CF6",
        anomalyPink: "#D946EF",
        advisorEmerald: "#10B981",
        advisorTeal: "#14B8A6",
        circadianIndigo: "#6366F1",
        circadianSky: "#38BDF8",
        envGold: "#EAB308",
        envOrange: "#F97316",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'cyan-glow': '0 0 15px -3px rgba(0, 240, 255, 0.25)',
        'crimson-glow': '0 0 15px -3px rgba(239, 68, 68, 0.25)',
        'amber-glow': '0 0 15px -3px rgba(245, 158, 11, 0.25)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      }
    },
  },
  plugins: [],
}
