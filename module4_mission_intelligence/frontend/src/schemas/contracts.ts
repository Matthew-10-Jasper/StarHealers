import { z } from 'zod';

export const OperationalStateSchema = z.enum([
  'NOMINAL',
  'DEGRADED',
  'CONTINGENCY',
  'UNKNOWN',
  'RECOVERY',
]);

export const DataSourceSchema = z.enum([
  'SIMULATED',
  'MANUAL_INPUT',
  'TELEMETRY',
  'EXTERNAL_REFERENCE',
]);

export const DeviationSeveritySchema = z.enum([
  'INFO',
  'WARNING',
  'CRITICAL',
  'UNKNOWN',
]);

export const QualityStatusSchema = z.enum([
  'VERIFIED',
  'UNVERIFIED',
  'STALE',
  'CONTRADICTORY',
  'INVALID_UNIT',
  'UNKNOWN',
]);

export const CommStatusSchema = z.enum([
  'OPTIMAL',
  'NOMINAL',
  'DELAYED',
  'INTERMITTENT',
  'DEGRADED',
  'BLACKOUT',
  'UNKNOWN',
]);

export const GravityEnvironmentSchema = z.enum([
  'MICROGRAVITY',
  'LUNAR_GRAVITY',
  'MARTIAN_GRAVITY',
  'EARTH_STANDARD',
  'CENTRIFUGAL_ARTIFICIAL',
  'UNKNOWN',
]);

export const CommunicationContextSchema = z.object({
  status: CommStatusSchema,
  expected_delay_seconds: z.number(),
  bandwidth_mbps: z.number(),
  earth_reachable: z.boolean(),
  queued_reports_count: z.number().default(0),
  last_contact_timestamp: z.string().nullable().default(null),
  last_acknowledged_timestamp: z.string().nullable().default(null),
});

export const EnvironmentStatusSchema = z.object({
  radiation_status: z.string().default('UNKNOWN'),
  cabin_pressure_status: z.string().default('UNKNOWN'),
  co2_status: z.string().default('UNKNOWN'),
  life_support_status: z.string().default('UNKNOWN'),
  habitat_status: z.string().default('UNKNOWN'),
  observed_parameters: z.record(z.string(), z.any()).default({}),
  parameter_timestamps: z.record(z.string(), z.string()).default({}),
});

export const DataQualityContextSchema = z.object({
  overall_status: QualityStatusSchema,
  unknown_parameters: z.array(z.string()).default([]),
  stale_parameters: z.array(z.string()).default([]),
  contradictory_parameters: z.array(z.string()).default([]),
  last_telemetry_timestamp: z.string().nullable().default(null),
});

export const MissionDeviationSchema = z.object({
  deviation_id: z.string(),
  deviation_name: z.string(),
  category: z.string(),
  expected_condition: z.string(),
  actual_condition: z.string(),
  evidence: z.record(z.string(), z.any()).default({}),
  severity: DeviationSeveritySchema,
  timestamp: z.string(),
  source: DataSourceSchema.default('SIMULATED'),
  confirmation_status: z.string().default('CONFIRMED'),
  resolved: z.boolean().default(false),
  resolution_notes: z.string().nullable().optional(),
});

export const MissionContextResponseSchema = z.object({
  context_id: z.string(),
  context_version: z.number(),
  mission_id: z.string(),
  planned_profile: z.string(),
  actual_mission_phase: z.string(),
  operational_state: OperationalStateSchema,
  gravity_environment: GravityEnvironmentSchema,
  gravity_value_g: z.number(),
  communication: CommunicationContextSchema,
  environment: EnvironmentStatusSchema,
  data_quality: DataQualityContextSchema,
  active_deviations: z.array(MissionDeviationSchema).default([]),
  data_source: DataSourceSchema.default('SIMULATED'),
  last_updated: z.string(),
});

import { MissionContextResponse } from '../types/mission';

export function parseMissionContext(rawData: unknown): MissionContextResponse {
  const result = MissionContextResponseSchema.safeParse(rawData);
  if (!result.success) {
    console.warn('MissionContext runtime contract validation warning:', result.error.format());
    return rawData as MissionContextResponse;
  }
  return result.data as unknown as MissionContextResponse;
}
