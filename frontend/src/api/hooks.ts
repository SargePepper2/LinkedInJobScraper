import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type ImportJobPayload, type ProfilePayload } from "./client";

export function useSummary() {
  return useQuery({
    queryKey: ["summary"],
    queryFn: () => api.getSummary(),
  });
}

export function useTrends(period = "weekly", limit = 10) {
  return useQuery({
    queryKey: ["trends", period, limit],
    queryFn: () => api.getTrends(period, limit),
  });
}

export function useSkillRankings(limit = 50) {
  return useQuery({
    queryKey: ["skill-rankings", limit],
    queryFn: () => api.getSkillRankings(limit),
  });
}

export function useCoOccurrences(minCount = 3) {
  return useQuery({
    queryKey: ["co-occurrences", minCount],
    queryFn: () => api.getCoOccurrences(minCount),
  });
}

export function useGapAnalysis(profileId: number) {
  return useQuery({
    queryKey: ["gap-analysis", profileId],
    queryFn: () => api.getGapAnalysis(profileId),
    enabled: profileId > 0,
  });
}

export function useProfileSuggestions(profileId: number) {
  return useQuery({
    queryKey: ["profile-suggestions", profileId],
    queryFn: () => api.getProfileSuggestions(profileId),
    enabled: profileId > 0,
  });
}

export function useJobs(limit = 50) {
  return useQuery({
    queryKey: ["jobs", limit],
    queryFn: () => api.getJobs(limit),
  });
}

export function useImportJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ImportJobPayload) => api.importJob(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["skill-rankings"] });
    },
  });
}

export function useImportCsv() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.importCsv(file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["skill-rankings"] });
    },
  });
}

export function useProfile(profileId: number) {
  return useQuery({
    queryKey: ["profile", profileId],
    queryFn: () => api.getProfile(profileId),
    enabled: profileId > 0,
  });
}

export function useCreateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProfilePayload) => api.createProfile(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}
