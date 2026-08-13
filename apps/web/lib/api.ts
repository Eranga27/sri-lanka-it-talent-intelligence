/**
 * API client — all data fetched server-side via Next.js RSC.
 * No mock fallbacks. Empty datasets return genuine empty states.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface JobsSummary {
  total_jobs: number;
  active_jobs: number;
  sri_lankan_jobs: number;
  last_ingested_at: string | null;
  data_available: boolean;
}

export interface RoleDistributionEntry {
  role_category: string | null;
  job_count: number;
}

export interface SourceEntry {
  source_id: string;
  source_name: string;
  owner: string;
  source_type: string;
  domain: string;
  geographic_scope: string;
  access_method: string;
  api_available: boolean;
  authentication_required: boolean;
  refresh_frequency: string;
  terms_status: string;
  reliability_score: number | null;
  integration_status: string;
  last_ingested_at: string | null;
  total_records_ingested: number;
  active_records: number;
  notes: string | null;
}

export interface JobRecord {
  job_id: string;
  source: string;
  source_job_id: string;
  company: string | null;
  title: string;
  location: string | null;
  country: string | null;
  department: string | null;
  role_category: string | null;
  classification_confidence: number | null;
  application_url: string | null;
  status: string;
  first_seen_at: string;
  last_seen_at: string;
  ingested_at: string;
}

export interface DataQualityInfo {
  data_available: boolean;
  total_records?: number;
  null_country_count?: number;
  unclassified_count?: number;
  null_description_count?: number;
  null_country_rate?: number;
  unclassified_rate?: number;
  last_ingested_at?: string | null;
  message?: string;
}

async function apiFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

export const api = {
  getJobsSummary: () => apiFetch<JobsSummary>("/api/jobs/summary"),
  getRoleDistribution: () => apiFetch<RoleDistributionEntry[]>("/api/roles/"),
  getSources: () => apiFetch<SourceEntry[]>("/api/sources/"),
  getJobs: (limit = 20, offset = 0) =>
    apiFetch<JobRecord[]>(`/api/jobs/?limit=${limit}&offset=${offset}`),
  getDataQuality: () => apiFetch<DataQualityInfo>("/api/data-quality/"),
};
