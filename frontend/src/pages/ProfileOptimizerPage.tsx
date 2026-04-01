import {
  Sparkles,
  MessageSquareText,
  Search,
  TrendingUp,
  Gauge,
} from "lucide-react";
import { useProfileSuggestions } from "@/api/hooks";

const PROFILE_ID = 1;

export default function ProfileOptimizerPage() {
  const { data, isLoading, error } = useProfileSuggestions(PROFILE_ID);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-6 text-red-300">
        Failed to load suggestions. Make sure your profile is set up.
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Profile Optimizer</h1>
        <p className="mt-1 text-gray-400">
          AI-powered suggestions to improve your LinkedIn profile
        </p>
      </div>

      {/* Optimization score */}
      <div className="flex items-center gap-6 rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-indigo-600/20 p-3">
            <Gauge className="h-8 w-8 text-indigo-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Optimization Score</p>
            <p className="text-3xl font-bold text-white">
              {data.optimization_score}
              <span className="text-lg text-gray-500">/100</span>
            </p>
          </div>
        </div>
        <div className="flex-1">
          <div className="h-3 overflow-hidden rounded-full bg-gray-800">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${data.optimization_score}%`,
                background: `linear-gradient(90deg, #6366f1, #a78bfa)`,
              }}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Headline suggestions */}
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
            <MessageSquareText className="h-5 w-5 text-purple-400" />
            Headline Suggestions
          </h2>
          <div className="space-y-3">
            {data.headline_suggestions.map((suggestion, i) => (
              <div
                key={i}
                className="rounded-lg border border-gray-800 bg-gray-800/40 p-4"
              >
                <div className="mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-amber-400" />
                  <span className="text-xs font-medium text-amber-400">
                    Suggestion {i + 1}
                  </span>
                </div>
                <p className="text-sm leading-relaxed text-gray-200">
                  {suggestion}
                </p>
              </div>
            ))}
            {data.headline_suggestions.length === 0 && (
              <p className="text-gray-500">No headline suggestions available.</p>
            )}
          </div>
        </div>

        {/* Missing keywords */}
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
            <Search className="h-5 w-5 text-blue-400" />
            Missing Keywords
          </h2>
          <p className="mb-3 text-sm text-gray-400">
            High-impact keywords that recruiters search for but are absent from
            your profile
          </p>
          <div className="flex flex-wrap gap-2">
            {data.missing_keywords.map((keyword) => (
              <span
                key={keyword}
                className="rounded-full border border-blue-800 bg-blue-950/40 px-3 py-1.5 text-sm text-blue-300"
              >
                {keyword}
              </span>
            ))}
            {data.missing_keywords.length === 0 && (
              <p className="text-gray-500">No missing keywords detected.</p>
            )}
          </div>
        </div>
      </div>

      {/* Trending skills */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
          <TrendingUp className="h-5 w-5 text-emerald-400" />
          Trending Skills to Learn
        </h2>
        <p className="mb-4 text-sm text-gray-400">
          Skills gaining traction in the job market that match your career
          trajectory
        </p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.trending_skills.map((skill, i) => (
            <div
              key={skill}
              className="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-800/40 p-3"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600/20 text-xs font-bold text-emerald-400">
                {i + 1}
              </div>
              <span className="text-sm font-medium text-gray-200">
                {skill}
              </span>
            </div>
          ))}
          {data.trending_skills.length === 0 && (
            <p className="text-gray-500">No trending skills identified yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
