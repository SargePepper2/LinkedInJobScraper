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

// --- Types ---

export interface Skill {
  id: number;
  name: string;
  category: string;
  frequency: number;
  percentage: number;
}

export interface SkillRankingsResponse {
  skills: Skill[];
  total_jobs: number;
  total_skills: number;
}

export interface CoOccurrence {
  skill_a: string;
  skill_b: string;
  count: number;
  correlation: number;
}

export interface GapAnalysisResponse {
  match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
  profile_skill_count: number;
  market_skill_count: number;
}

export interface ProfileSuggestion {
  headline_suggestions: string[];
  missing_keywords: string[];
  trending_skills: string[];
  optimization_score: number;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  skills: string[];
  imported_at: string;
}

export interface ImportJobPayload {
  title: string;
  company: string;
  description: string;
}

export interface Profile {
  id: number;
  name: string;
  headline: string;
  skills: string[];
}

export interface ProfilePayload {
  name: string;
  headline: string;
  skills: string[];
}

// --- API functions ---

export const api = {
  getSkillRankings: (category?: string) =>
    request<SkillRankingsResponse>(
      `/skills/rankings${category ? `?category=${encodeURIComponent(category)}` : ""}`,
    ),

  getCoOccurrences: (minCount = 2) =>
    request<CoOccurrence[]>(`/skills/co-occurrences?min_count=${minCount}`),

  getGapAnalysis: (profileId: number) =>
    request<GapAnalysisResponse>(`/profiles/${profileId}/gap-analysis`),

  getProfileSuggestions: (profileId: number) =>
    request<ProfileSuggestion>(`/profiles/${profileId}/suggestions`),

  getJobs: (limit = 50) =>
    request<Job[]>(`/jobs?limit=${limit}`),

  importJob: (payload: ImportJobPayload) =>
    request<Job>("/jobs/import", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  importCsv: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ imported: number }>("/jobs/import/csv", {
      method: "POST",
      body: formData,
      headers: {},
    });
  },

  getProfile: (profileId: number) =>
    request<Profile>(`/profiles/${profileId}`),

  createProfile: (payload: ProfilePayload) =>
    request<Profile>("/profiles", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateProfile: (profileId: number, payload: ProfilePayload) =>
    request<Profile>(`/profiles/${profileId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
