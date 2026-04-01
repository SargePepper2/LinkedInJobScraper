const BASE_URL = "/api";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, body);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// --- Types (matching actual backend responses) ---

export interface SkillRanking {
  name: string;
  category: string;
  count: number;
  percentage: number;
}

export interface CoOccurrence {
  skill_a: string;
  skill_b: string;
  count: number;
}

export interface GapAnalysisResponse {
  match_percentage: number;
  matching_skills: string[];
  missing_skills: { name: string; category: string; count: number; percentage: number }[];
  undervalued_skills: string[];
  high_value_skills: string[];
  top_recommendations: string[];
}

export interface ProfileSuggestionResponse {
  headline_options: string[];
  missing_keywords: string[];
  trending_skills: string[];
}

export interface JobResponse {
  id: number;
  title: string;
  company: string | null;
  location: string | null;
  source: string;
  skills_found: number;
}

export interface ImportJobPayload {
  title: string;
  company?: string;
  description: string;
}

export interface ProfileResponse {
  id: number;
  name: string;
  target_role: string | null;
  headline: string | null;
  skills: string[];
}

export interface ProfilePayload {
  name: string;
  target_role?: string;
  headline?: string;
  summary?: string;
  skill_names: string[];
}

export interface TrendDataPoint {
  date: string;
  count: number;
}

export interface SkillTrend {
  skill_name: string;
  periods: TrendDataPoint[];
}

export interface SummaryStats {
  total_jobs: number;
  total_skills: number;
  top_category: string;
  avg_skills_per_job: number;
  sources: { source: string; count: number }[];
}

// --- API functions (matching actual backend routes) ---

export const api = {
  // GET /api/skills/rankings?limit=50
  getSkillRankings: (limit = 50) =>
    request<SkillRanking[]>(`/skills/rankings?limit=${limit}`),

  // GET /api/skills/co-occurrence?min_count=3&limit=50
  getCoOccurrences: (minCount = 3) =>
    request<CoOccurrence[]>(`/skills/co-occurrence?min_count=${minCount}`),

  // GET /api/analysis/gap/{profileId}
  getGapAnalysis: (profileId: number) =>
    request<GapAnalysisResponse>(`/analysis/gap/${profileId}`),

  // GET /api/analysis/profile-suggestions/{profileId}
  getProfileSuggestions: (profileId: number) =>
    request<ProfileSuggestionResponse>(`/analysis/profile-suggestions/${profileId}`),

  // GET /api/jobs/?limit=50
  getJobs: (limit = 50) =>
    request<JobResponse[]>(`/jobs/?skip=0&limit=${limit}`),

  // POST /api/jobs/import/paste
  importJob: (payload: ImportJobPayload) =>
    request<JobResponse>("/jobs/import/paste", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // POST /api/jobs/import/csv
  importCsv: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ imported: number }>("/jobs/import/csv", {
      method: "POST",
      body: formData,
      headers: {},
    });
  },

  // GET /api/profile/{profileId}
  getProfile: (profileId: number) =>
    request<ProfileResponse>(`/profile/${profileId}`),

  // POST /api/profile/
  createProfile: (payload: ProfilePayload) =>
    request<ProfileResponse>("/profile/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // POST /api/profile/{profileId}/skills
  addSkills: (profileId: number, skillNames: string[]) =>
    request<{ added: string[] }>(`/profile/${profileId}/skills`, {
      method: "POST",
      body: JSON.stringify({ skill_names: skillNames }),
    }),

  // GET /api/analysis/summary
  getSummary: () => request<SummaryStats>("/analysis/summary"),

  // GET /api/analysis/trends
  getTrends: (period = "weekly", limit = 10) =>
    request<SkillTrend[]>(`/analysis/trends?period=${period}&limit=${limit}`),
};
