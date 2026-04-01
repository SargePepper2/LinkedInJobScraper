import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type ImportJobPayload, type ProfilePayload } from "./client";

export function useSkillRankings(category?: string) {
  return useQuery({
    queryKey: ["skill-rankings", category],
    queryFn: () => api.getSkillRankings(category),
  });
}

export function useCoOccurrences(minCount = 2) {
  return useQuery({
    queryKey: ["co-occurrences", minCount],
    queryFn: () => api.getCoOccurrences(minCount),
  });
}

export function useGapAnalysis(profileId: number) {
  return useQuery({
    queryKey: ["gap-analysis", profileId],
    queryFn: () => api.getGapAnalysis(profileId),
  });
}

export function useProfileSuggestions(profileId: number) {
  return useQuery({
    queryKey: ["profile-suggestions", profileId],
    queryFn: () => api.getProfileSuggestions(profileId),
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

export function useUpdateProfile(profileId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProfilePayload) =>
      api.updateProfile(profileId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["profile", profileId] });
      void queryClient.invalidateQueries({ queryKey: ["gap-analysis"] });
      void queryClient.invalidateQueries({ queryKey: ["profile-suggestions"] });
    },
  });
}
