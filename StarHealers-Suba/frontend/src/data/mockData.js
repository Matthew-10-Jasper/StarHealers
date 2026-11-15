// StarHealers Mock Physiological & Mission Data Engine
// Supports ISS, Moon (Artemis), and Mars missions with realistic baseline physiological telemetry

export const MISSIONS = [
  {
    id: "mission-mars-01",
    name: "Ares V — Mars Transit",
    target: "Mars",
    phase: "Deep Space Cruise (Day 142)",
    commsDelaySec: 840, // 14 mins delay
    environment: {
      cabinCo2: "0.42%", // Normal < 0.5%
      cabinO2: "20.9%",
      cabinPressure: "101.3 kPa",
      ambientTemp: "21.4 °C",
      radiationDoseRate: "1.82 mSv/day",
      gravity: "0.00 g (Microgravity)",
    },
    status: "ACTIVE",
    crewCount: 4,
  },
  {
    id: "mission-artemis-03",
    name: "Artemis IV — Lunar Outpost",
    target: "Moon",
    phase: "South Pole Surface Ops",
    commsDelaySec: 1.3,
    environment: {
      cabinCo2: "0.35%",
      cabinO2: "21.0%",
      cabinPressure: "101.1 kPa",
      ambientTemp: "22.0 °C",
      radiationDoseRate: "0.75 mSv/day",
      gravity: "0.16 g (Lunar)",
    },
    status: "STANDBY",
    crewCount: 4,
  },
  {
    id: "mission-iss-exp72",
    name: "ISS Expedition 72",
    target: "Low Earth Orbit",
    phase: "Orbital Laboratory",
    commsDelaySec: 0.4,
    environment: {
      cabinCo2: "0.28%",
      cabinO2: "21.2%",
      cabinPressure: "101.3 kPa",
      ambientTemp: "22.5 °C",
      radiationDoseRate: "0.45 mSv/day",
      gravity: "0.00 g (LEO)",
    },
    status: "ACTIVE",
    crewCount: 4,
  },
];

export const ASTRONAUTS = [
  {
    id: "ASTRO-01",
    name: "Dr. Sarah Chen",
    role: "Commander & Astrobiologist",
    missionId: "mission-mars-01",
    age: 38,
    bloodType: "A+",
    heightCm: 168,
    weightKg: 61,
    avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
    status: "WARNING", // Yellow/Amber
    statusReason: "Elevated heart rate, reduced HRV & acute cumulative sleep deficit",
    baseline: {
      restingHr: 62,
      hrv: 68,
      bpSystolic: 114,
      bpDiastolic: 74,
      spo2: 98,
      temp: 36.6,
      glucose: 92,
      hydration: 62,
      stress: 28,
    },
    bodyRegionStatus: {
      brain: "WARNING",
      heart: "WARNING",
      lungs: "NORMAL",
      musculoskeletal: "NORMAL",
      immune: "NORMAL",
      metabolic: "NORMAL",
    },
  },
  {
    id: "ASTRO-02",
    name: "Cmdr. Marcus Vance",
    role: "Pilot & Flight Systems Lead",
    missionId: "mission-mars-01",
    age: 42,
    bloodType: "O+",
    heightCm: 182,
    weightKg: 79,
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
    status: "NORMAL", // Green
    statusReason: "All physiological telemetry within nominal baselines",
    baseline: {
      restingHr: 58,
      hrv: 74,
      bpSystolic: 118,
      bpDiastolic: 76,
      spo2: 99,
      temp: 36.5,
      glucose: 95,
      hydration: 64,
      stress: 22,
    },
    bodyRegionStatus: {
      brain: "NORMAL",
      heart: "NORMAL",
      lungs: "NORMAL",
      musculoskeletal: "NORMAL",
      immune: "NORMAL",
      metabolic: "NORMAL",
    },
  },
  {
    id: "ASTRO-03",
    name: "Dr. Elena Rostova",
    role: "Flight Surgeon & Medical Officer",
    missionId: "mission-mars-01",
    age: 36,
    bloodType: "B+",
    heightCm: 172,
    weightKg: 64,
    avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
    status: "CRITICAL", // Red - Hypoxia simulation
    statusReason: "Acute SpO2 drop (91%) with elevated compensatory heart rate",
    baseline: {
      restingHr: 60,
      hrv: 65,
      bpSystolic: 116,
      bpDiastolic: 75,
      spo2: 98,
      temp: 36.7,
      glucose: 88,
      hydration: 60,
      stress: 25,
    },
    bodyRegionStatus: {
      brain: "WARNING",
      heart: "CRITICAL",
      lungs: "CRITICAL",
      musculoskeletal: "NORMAL",
      immune: "NORMAL",
      metabolic: "NORMAL",
    },
  },
  {
    id: "ASTRO-04",
    name: "Alex Tanaka",
    role: "Payload & Robotics Specialist",
    missionId: "mission-mars-01",
    age: 31,
    bloodType: "AB-",
    heightCm: 175,
    weightKg: 68,
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
    status: "NO_DATA", // Grey
    statusReason: "Telemetry sensor link recalibrating; biometric data packet deferred",
    baseline: {
      restingHr: 64,
      hrv: 62,
      bpSystolic: 120,
      bpDiastolic: 78,
      spo2: 98,
      temp: 36.6,
      glucose: 90,
      hydration: 59,
      stress: 30,
    },
    bodyRegionStatus: {
      brain: "NO_DATA",
      heart: "NO_DATA",
      lungs: "NO_DATA",
      musculoskeletal: "NO_DATA",
      immune: "NO_DATA",
      metabolic: "NO_DATA",
    },
  },
];

// Reference ranges for all monitored physiological parameters
export const METRIC_DEFINITIONS = {
  heartRate: {
    id: "heartRate",
    label: "Heart Rate",
    unit: "bpm",
    normalMin: 60,
    normalMax: 100,
    warningMin: 50,
    warningMax: 115,
    bodyRegion: "Heart",
    description: "Cardiovascular contractile frequency and cardiac output indicator",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  hrv: {
    id: "hrv",
    label: "Heart Rate Variability (RMSSD)",
    unit: "ms",
    normalMin: 45,
    normalMax: 110,
    warningMin: 30,
    warningMax: 45,
    bodyRegion: "Heart",
    description: "Autonomic nervous system balance and physiological stress reserve",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  bloodPressure: {
    id: "bloodPressure",
    label: "Blood Pressure",
    unit: "mmHg",
    systolicMin: 90,
    systolicMax: 130,
    diastolicMin: 60,
    diastolicMax: 85,
    bodyRegion: "Heart",
    description: "Circulatory systemic perfusion and vascular resistance",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  spo2: {
    id: "spo2",
    label: "Oxygen Saturation (SpO2)",
    unit: "%",
    normalMin: 95,
    normalMax: 100,
    warningMin: 92,
    warningMax: 94,
    criticalMin: 0,
    criticalMax: 91,
    bodyRegion: "Lungs",
    description: "Peripheral arterial blood hemoglobin oxygenation level",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  temperature: {
    id: "temperature",
    label: "Skin / Core Temp",
    unit: "°C",
    normalMin: 36.1,
    normalMax: 37.3,
    warningMin: 35.8,
    warningMax: 38.0,
    bodyRegion: "Metabolic System",
    description: "Thermoregulatory balance and systemic inflammatory status",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  glucose: {
    id: "glucose",
    label: "Blood Glucose",
    unit: "mg/dL",
    normalMin: 70,
    normalMax: 120,
    warningMin: 60,
    warningMax: 140,
    bodyRegion: "Metabolic System",
    description: "Circulating metabolic substrate and cellular energy availability",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  sleep: {
    id: "sleep",
    label: "Sleep Duration (24h)",
    unit: "hrs",
    normalMin: 7.0,
    normalMax: 9.0,
    warningMin: 5.0,
    warningMax: 6.9,
    bodyRegion: "Brain and Eyes",
    description: "Restorative sleep architecture and neuro-cognitive recovery",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  hydration: {
    id: "hydration",
    label: "Hydration Level",
    unit: "%",
    normalMin: 55,
    normalMax: 68,
    warningMin: 48,
    warningMax: 54,
    bodyRegion: "Metabolic System",
    description: "Estimated total body water and vascular fluid equilibrium",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
  stress: {
    id: "stress",
    label: "Physiological Stress Index",
    unit: "pts",
    normalMin: 0,
    normalMax: 35,
    warningMin: 36,
    warningMax: 65,
    bodyRegion: "Brain and Eyes",
    description: "Composite metric from sympathetic tone, speech biomarkers & self-report",
    palette: { primary: "#00F0FF", secondary: "#3B82F6" },
  },
};

// Current readings by Astronaut ID
export const CURRENT_READINGS = {
  "ASTRO-01": {
    heartRate: { value: 94, unit: "bpm", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "WARNING" },
    hrv: { value: 34, unit: "ms", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "WARNING" },
    bloodPressure: { systolic: 136, diastolic: 88, unit: "mmHg", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:40:00Z", status: "WARNING" },
    spo2: { value: 97, unit: "%", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    temperature: { value: 37.1, unit: "°C", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    glucose: { value: 104, unit: "mg/dL", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T14:30:00Z", status: "NORMAL" },
    sleep: { value: 4.8, unit: "hrs", source: "CONNECTED SENSOR", quality: "HIGH", timestamp: "2026-11-15T08:00:00Z", status: "WARNING" },
    hydration: { value: 58, unit: "%", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:00:00Z", status: "NORMAL" },
    stress: { value: 72, unit: "pts", source: "RESEARCH DATASET", quality: "VALIDATED", timestamp: "2026-11-15T15:30:00Z", status: "WARNING" },
  },
  "ASTRO-02": {
    heartRate: { value: 64, unit: "bpm", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    hrv: { value: 76, unit: "ms", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    bloodPressure: { systolic: 118, diastolic: 76, unit: "mmHg", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:40:00Z", status: "NORMAL" },
    spo2: { value: 99, unit: "%", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    temperature: { value: 36.6, unit: "°C", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:45:00Z", status: "NORMAL" },
    glucose: { value: 94, unit: "mg/dL", source: "MANUAL INPUT", quality: "VERIFIED", timestamp: "2026-11-15T13:00:00Z", status: "NORMAL" },
    sleep: { value: 7.9, unit: "hrs", source: "CONNECTED SENSOR", quality: "HIGH", timestamp: "2026-11-15T08:00:00Z", status: "NORMAL" },
    hydration: { value: 63, unit: "%", source: "CONNECTED SENSOR", quality: "EXCELLENT", timestamp: "2026-11-15T15:00:00Z", status: "NORMAL" },
    stress: { value: 24, unit: "pts", source: "CONNECTED SENSOR", quality: "HIGH", timestamp: "2026-11-15T15:30:00Z", status: "NORMAL" },
  },
  "ASTRO-03": {
    heartRate: { value: 112, unit: "bpm", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "CRITICAL" },
    hrv: { value: 26, unit: "ms", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "CRITICAL" },
    bloodPressure: { systolic: 142, diastolic: 92, unit: "mmHg", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:40:00Z", status: "CRITICAL" },
    spo2: { value: 90, unit: "%", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "CRITICAL" },
    temperature: { value: 37.4, unit: "°C", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:45:00Z", status: "WARNING" },
    glucose: { value: 110, unit: "mg/dL", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T14:30:00Z", status: "NORMAL" },
    sleep: { value: 6.2, unit: "hrs", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T08:00:00Z", status: "WARNING" },
    hydration: { value: 54, unit: "%", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:00:00Z", status: "WARNING" },
    stress: { value: 84, unit: "pts", source: "SIMULATED", quality: "GOOD", timestamp: "2026-11-15T15:30:00Z", status: "CRITICAL" },
  },
  "ASTRO-04": {
    heartRate: { value: null, unit: "bpm", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    hrv: { value: null, unit: "ms", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    bloodPressure: { systolic: null, diastolic: null, unit: "mmHg", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    spo2: { value: null, unit: "%", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    temperature: { value: null, unit: "°C", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    glucose: { value: null, unit: "mg/dL", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    sleep: { value: null, unit: "hrs", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T08:00:00Z", status: "NO_DATA" },
    hydration: { value: null, unit: "%", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
    stress: { value: null, unit: "pts", source: "SIMULATED", quality: "UNAVAILABLE", timestamp: "2026-11-15T15:00:00Z", status: "NO_DATA" },
  },
};

// Generates time-series historical telemetry for charts
export function generateHistoricalData(astronautId, timeRange = "24h") {
  const points = timeRange === "1h" ? 20 : timeRange === "24h" ? 24 : timeRange === "7d" ? 28 : 35;
  const astro = ASTRONAUTS.find((a) => a.id === astronautId) || ASTRONAUTS[0];
  const isSarah = astronautId === "ASTRO-01";
  const isElena = astronautId === "ASTRO-03";
  const isAlex = astronautId === "ASTRO-04";

  if (isAlex) {
    return Array.from({ length: points }, (_, i) => ({
      time: timeRange === "1h" ? `${i * 3}m` : timeRange === "24h" ? `${i}:00` : `Day ${Math.floor(i / 4) + 1}`,
      heartRate: null,
      hrv: null,
      spo2: null,
      temperature: null,
      stress: null,
    }));
  }

  return Array.from({ length: points }, (_, i) => {
    const fraction = i / points;
    let hrOffset = 0;
    let hrvOffset = 0;
    let spo2Offset = 0;
    let stressOffset = 0;

    if (isSarah) {
      // Gradual fatigue progression
      hrOffset = fraction * 26 + Math.sin(i) * 4;
      hrvOffset = -fraction * 32 + Math.cos(i) * 3;
      stressOffset = fraction * 40 + Math.sin(i * 1.5) * 5;
    } else if (isElena) {
      // Acute sudden hypoxia event towards the end
      if (fraction > 0.65) {
        spo2Offset = -((fraction - 0.65) * 20);
        hrOffset = (fraction - 0.65) * 45;
        hrvOffset = -((fraction - 0.65) * 35);
        stressOffset = (fraction - 0.65) * 55;
      }
    } else {
      // Marcus: Stable baseline oscillation
      hrOffset = Math.sin(i * 0.8) * 5;
      hrvOffset = Math.cos(i * 0.8) * 6;
      stressOffset = Math.sin(i) * 4;
    }

    return {
      time: timeRange === "1h" ? `${i * 3}m ago` : timeRange === "24h" ? `${i < 10 ? '0' + i : i}:00` : `Day ${Math.floor(i / 4) + 1}`,
      heartRate: Math.round(astro.baseline.restingHr + hrOffset),
      hrv: Math.max(18, Math.round(astro.baseline.hrv + hrvOffset)),
      spo2: Math.min(100, Math.max(88, Math.round(astro.baseline.spo2 + spo2Offset))),
      temperature: Number((astro.baseline.temp + (Math.sin(i) * 0.15)).toFixed(1)),
      stress: Math.min(100, Math.max(10, Math.round(astro.baseline.stress + stressOffset))),
      source: "SIMULATED",
    };
  });
}

// Active and historical rule-based triage alerts
export const TRIAGE_ALERTS = [
  {
    id: "ALT-2026-0891",
    astronautId: "ASTRO-03",
    severity: "CRITICAL", // Red
    title: "Acute Hypoxic Respiratory Depletion",
    timestamp: "2026-11-15T15:42:10Z",
    status: "ACTIVE",
    ruleId: "RULE-HYPOXIA-ACUTE-01",
    triggerReason: "Arterial SpO2 fell below critical threshold (< 92%) with concurrent tachycardia (> 110 bpm) under microgravity environment.",
    contributingMeasurements: [
      { name: "SpO2", value: "90%", threshold: "< 92%", unit: "%", status: "CRITICAL" },
      { name: "Heart Rate", value: "112 bpm", threshold: "> 105 bpm", unit: "bpm", status: "CRITICAL" },
      { name: "Cabin CO2", value: "0.42%", threshold: "< 0.50%", unit: "%", status: "NORMAL" },
    ],
    explanation: "Hypoxemia detected. The astronaut's blood oxygen saturation has dropped significantly below acceptable deep-space physiological tolerance. Concomitant elevated heart rate indicates compensatory cardiac drive attempting to preserve peripheral perfusion. Not an automated diagnosis of pathology; rule indicates immediate respiratory protocol escalation.",
    escalationSteps: [
      "Immediate crew cross-check of portable O2 mask system",
      "Verify suit/helmet air scrubbers and cabin ventilation loop",
      "Perform bedside lung auscultation and pulse oximeter probe re-seat",
      "Prepare autonomous Medical Kit Bravo (Bronchodilator / O2 supply)",
    ],
    acknowledgedBy: null,
  },
  {
    id: "ALT-2026-0888",
    astronautId: "ASTRO-01",
    severity: "WARNING", // Amber
    title: "Multi-Signal Autonomic Fatigue Pattern",
    timestamp: "2026-11-15T14:15:22Z",
    status: "ACTIVE",
    ruleId: "RULE-FATIGUE-COMPOUND-03",
    triggerReason: "Combined detection of suppressed vagal HRV (< 40 ms), chronic sleep truncation (< 5.0 hrs), and sympathetic hyper-reactivity (Stress > 70 pts).",
    contributingMeasurements: [
      { name: "Heart Rate Variability", value: "34 ms", threshold: "< 40 ms (Baseline: 68 ms)", unit: "ms", status: "WARNING" },
      { name: "24h Sleep Duration", value: "4.8 hrs", threshold: "< 6.0 hrs", unit: "hrs", status: "WARNING" },
      { name: "Physiological Stress", value: "72 pts", threshold: "> 65 pts", unit: "pts", status: "WARNING" },
      { name: "Resting Heart Rate", value: "94 bpm", threshold: "> 85 bpm (Resting)", unit: "bpm", status: "WARNING" },
    ],
    explanation: "Multi-parameter autonomic imbalance. Chronic circadian disruption and sleep deprivation are producing cumulative autonomic strain. Cardiac vagal tone is suppressed by 50% relative to baseline, elevating cognitive lapse risk during critical mission maneuvers.",
    escalationSteps: [
      "Recommend 90-minute restorative sleep block prior to EVA duties",
      "Review cognitive workload and schedule non-critical task deferrals",
      "Administer scheduled blue-wavelength light therapy attenuation",
      "Log PVT (Psychomotor Vigilance Task) assessment at next duty station",
    ],
    acknowledgedBy: "Medical Officer Suba",
  },
  {
    id: "ALT-2026-0872",
    astronautId: "ASTRO-01",
    severity: "WARNING",
    title: "Elevated Systolic Blood Pressure Trend",
    timestamp: "2026-11-14T20:10:05Z",
    status: "RESOLVED",
    ruleId: "RULE-CARDIO-BP-02",
    triggerReason: "Blood pressure reading exceeded stage-1 threshold (136/88 mmHg).",
    contributingMeasurements: [
      { name: "Blood Pressure", value: "136/88 mmHg", threshold: "> 130/85 mmHg", unit: "mmHg", status: "WARNING" },
    ],
    explanation: "Temporary cardiovascular stress response observed post-cycle ergometer resistance exercise protocol. Stabilized upon scheduled rest period.",
    escalationSteps: [
      "Repeat manual cuff measurement at rest",
      "Hydration check verified nominal",
    ],
    acknowledgedBy: "Cmdr. Marcus Vance",
  },
  {
    id: "ALT-2026-0865",
    astronautId: "ASTRO-04",
    severity: "NO_DATA",
    title: "Telemetry Signal Loss — Biometric Node 4",
    timestamp: "2026-11-15T15:02:11Z",
    status: "ACTIVE",
    ruleId: "RULE-SENSOR-LINK-01",
    triggerReason: "Continuous missing data packets exceeding 30 minutes from wearable telemetry suite.",
    contributingMeasurements: [
      { name: "Sensor Packet Loss", value: "100%", threshold: "> 25%", unit: "%", status: "NO_DATA" },
      { name: "Last Heartbeat", value: "43m ago", threshold: "> 15m", unit: "time", status: "NO_DATA" },
    ],
    explanation: "Astronaut biometric hub is offline or undergoing scheduled recharging. Telemetry triage marked as NO DATA rather than normal to prevent false assurance.",
    escalationSteps: [
      "Prompt crew member to check wearable sensor power status",
      "Verify habitat wireless transponder link",
    ],
    acknowledgedBy: null,
  },
];

// Interactive Body Map Region Configuration
export const BODY_REGIONS_CONFIG = {
  brain: {
    id: "brain",
    label: "Brain & Eyes",
    subsystems: ["Neuro-Cognitive", "Circadian Rhythm", "Sensory (Visual)"],
    associatedMetrics: ["sleep", "stress"],
    description: "Monitors sleep duration, fatigue debt, ocular intracranial fluid pressure indicators, and physiological stress tone.",
    disclaimer: "Body map associations correlate biometric signals with anatomical systems for situational awareness; this does not constitute a diagnostic imaging scan.",
  },
  heart: {
    id: "heart",
    label: "Cardiovascular (Heart)",
    subsystems: ["Cardiac Myocardium", "Autonomic Sinus Rhythm", "Systemic Hemodynamics"],
    associatedMetrics: ["heartRate", "hrv", "bloodPressure"],
    description: "Evaluates cardiac chronotropic response, parasympathetic HRV tone, and arterial blood pressure dynamics in altered gravity.",
    disclaimer: "Hemodynamic fluctuations in microgravity are influenced by cephalad fluid shifts. Elevated readings require rest-standardized clinical verification.",
  },
  lungs: {
    id: "lungs",
    label: "Respiratory (Lungs)",
    subsystems: ["Pulmonary Gas Exchange", "Arterial O2 Saturation", "Environmental CO2 Scrubbing"],
    associatedMetrics: ["spo2"],
    description: "Monitors blood oxygen saturation (SpO2) and pulmonary gas diffusion efficiency, cross-referenced with habitat cabin CO2.",
    disclaimer: "Low SpO2 alerts indicate immediate oxygenation concern but require clinical inspection to distinguish sensor displacement from pulmonary pathology.",
  },
  musculoskeletal: {
    id: "musculoskeletal",
    label: "Musculoskeletal System",
    subsystems: ["Bone Mineral Density", "Postural Muscle Atrophy", "Exercise Countermeasures"],
    associatedMetrics: ["temperature"], // + future exercise telemetry
    description: "Tracks physical exercise compliance, deep-tissue strain, core thermogenesis, and microgravity neuromuscular deconditioning.",
    disclaimer: "Long-duration spaceflight induces bone calcium loss and extensor muscle atrophy. Countermeasure compliance is required for mission readiness.",
  },
  immune: {
    id: "immune",
    label: "Immune & Hematologic",
    subsystems: ["Cellular Immunity", "Latent Viral Reactivation", "Radiation Susceptibility"],
    associatedMetrics: ["temperature", "stress"],
    description: "Observes peripheral temperature spikes, persistent inflammatory stress markers, and radiation-induced cellular stress vulnerabilities.",
    disclaimer: "Spaceflight dysregulates T-cell function and cytokine release. Observed indicators require clinical blood laboratory confirmation.",
  },
  metabolic: {
    id: "metabolic",
    label: "Metabolic & Renal",
    subsystems: ["Glycemic Equilibrium", "Hydration Balance", "Thermoregulation"],
    associatedMetrics: ["glucose", "hydration", "temperature"],
    description: "Supervises nutritional caloric status, glucose stability, electrolyte hydration balance, and renal fluid shifts.",
    disclaimer: "Hydration calculations are estimated from bioimpedance and intake logs. Not an automated diagnosis of renal pathology.",
  },
};
