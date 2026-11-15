export type OperationalState = 'NOMINAL' | 'DEGRADED' | 'CONTINGENCY' | 'UNKNOWN' | 'RECOVERY';

export type DataSource = 'SIMULATED' | 'MANUAL_INPUT' | 'TELEMETRY' | 'EXTERNAL_REFERENCE';

export type DeviationSeverity = 'INFO' | 'WARNING' | 'CRITICAL' | 'UNKNOWN';

export type QualityStatus = 'VERIFIED' | 'PARTIAL' | 'UNVERIFIED' | 'STALE' | 'CONTRADICTORY' | 'INVALID_UNIT' | 'UNKNOWN';

export type CommStatus = 'OPTIMAL' | 'NOMINAL' | 'DELAYED' | 'INTERMITTENT' | 'DEGRADED' | 'BLACKOUT' | 'UNKNOWN';

export type GravityEnvironment = 'MICROGRAVITY' | 'LUNAR_GRAVITY' | 'MARTIAN_GRAVITY' | 'EARTH_STANDARD' | 'CENTRIFUGAL_ARTIFICIAL' | 'UNKNOWN';

export interface ParameterBound {
  min: number;
  max: number;
  target: number;
}

export interface CommunicationCharacteristics {
  link_type: string;
  expected_delay_seconds: number;
  bandwidth_mbps: number;
  reachability: string;
}

export interface MissionProfile {
  mission_id: string;
  mission_name: string;
  destination: string;
  mission_phase: string;
  gravity_environment: GravityEnvironment;
  gravity_value_g: number;
  habitat_type: string;
  expected_duration_days?: number;
  communication_characteristics: CommunicationCharacteristics;
  environmental_monitoring_categories: string[];
  nominal_bounds: Record<string, ParameterBound>;
  configuration_version: string;
  data_source: DataSource;
}

export interface CommunicationContext {
  status: CommStatus;
  expected_delay_seconds: number;
  bandwidth_mbps: number;
  earth_reachable: boolean;
  queued_reports_count: number;
  last_contact_timestamp: string | null;
  last_acknowledged_timestamp: string | null;
}

export interface EnvironmentStatus {
  radiation_status: string;
  cabin_pressure_status: string;
  co2_status: string;
  life_support_status: string;
  habitat_status: string;
  observed_parameters: Record<string, any>;
  parameter_timestamps: Record<string, string>;
}

export interface DataQualityContext {
  overall_status: QualityStatus;
  validation_quality?: QualityStatus;
  telemetry_completeness?: 'COMPLETE' | 'PARTIAL' | 'NONE';
  telemetry_freshness?: 'FRESH' | 'STALE' | 'UNKNOWN';
  unknown_parameters: string[];
  stale_parameters: string[];
  contradictory_parameters: string[];
  last_telemetry_timestamp: string | null;
}

export interface MissionDeviation {
  deviation_id: string;
  deviation_name: string;
  category: string;
  expected_condition: string;
  actual_condition: string;
  evidence: Record<string, any>;
  severity: DeviationSeverity;
  timestamp: string;
  source: DataSource;
  confirmation_status: string;
  resolved: boolean;
  resolution_notes?: string | null;
}

export interface MissionContextResponse {
  context_id: string;
  context_version: number;
  mission_id: string;
  planned_profile: string;
  actual_mission_phase: string;
  operational_state: OperationalState;
  gravity_environment: GravityEnvironment;
  gravity_value_g: number;
  communication: CommunicationContext;
  environment: EnvironmentStatus;
  data_quality: DataQualityContext;
  active_deviations: MissionDeviation[];
  data_source: DataSource;
  last_updated: string;
}

export interface AuditEvent {
  event_id: string;
  event_type: string;
  description: string;
  evidence: Record<string, any>;
  operator_id: string;
  context_version: number;
  timestamp: string;
}

export interface StateTransitionRecord {
  transition_id: string;
  from_state: OperationalState;
  to_state: OperationalState;
  reason: string;
  evidence: Record<string, any>;
  operator_id: string;
  is_valid: boolean;
  context_version: number;
  timestamp: string;
}

export interface MissionHistoryResponse {
  audit_events: AuditEvent[];
  state_transitions: StateTransitionRecord[];
}

