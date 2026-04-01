import { CheckCircle2, XCircle, Lightbulb, TrendingUp } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { useGapAnalysis } from "@/api/hooks";

const PROFILE_ID = 1;

export default function GapAnalysisPage() {
  const { data, isLoading, error } = useGapAnalysis(PROFILE_ID);

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
        Failed to load gap analysis. Make sure you have a profile set up.
      </div>
    );
  }

  if (!data) return null;

  const pieData = [
    { name: "Matching", value: data.matching_skills.length },
    { name: "Missing", value: data.missing_skills.length },
  ];
  const PIE_COLORS = ["#22c55e", "#ef4444"];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Gap Analysis</h1>
        <p className="mt-1 text-gray-400">
          How your skills compare to market demand
        </p>
      </div>

      {/* Match score + pie chart */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Score card */}
        <div className="flex flex-col items-center justify-center rounded-xl border border-gray-800 bg-gray-900 p-8">
          <div className="relative flex h-36 w-36 items-center justify-center">
            <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#374151"
                strokeWidth="8"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke={data.match_percentage >= 70 ? "#22c55e" : data.match_percentage >= 40 ? "#eab308" : "#ef4444"}
                strokeWidth="8"
                strokeDasharray={`${data.match_percentage * 2.51} 999`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-3xl font-bold text-white">
              {data.match_percentage}%
            </span>
          </div>
          <p className="mt-4 text-sm text-gray-400">Overall Match Score</p>
        </div>

        {/* Pie chart */}
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h3 className="mb-2 text-sm font-medium text-gray-400">
            Skills Breakdown
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={4}
                dataKey="value"
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f3f4f6",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex justify-center gap-6 text-xs">
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-green-500" />
              Matching ({data.matching_skills.length})
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
              Missing ({data.missing_skills.length})
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex flex-col gap-4">
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
            <p className="text-sm text-gray-400">Your Skills</p>
            <p className="mt-1 text-2xl font-bold text-white">
              {data.profile_skill_count}
            </p>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
            <p className="text-sm text-gray-400">Market Skills Tracked</p>
            <p className="mt-1 text-2xl font-bold text-white">
              {data.market_skill_count}
            </p>
          </div>
        </div>
      </div>

      {/* Matching skills */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-green-400">
          <CheckCircle2 className="h-5 w-5" />
          Matching Skills
        </h2>
        <div className="flex flex-wrap gap-2">
          {data.matching_skills.map((skill) => (
            <span
              key={skill}
              className="rounded-full border border-green-800 bg-green-950/40 px-3 py-1.5 text-sm text-green-300"
            >
              {skill}
            </span>
          ))}
          {data.matching_skills.length === 0 && (
            <p className="text-gray-500">No matching skills found yet.</p>
          )}
        </div>
      </div>

      {/* Missing skills */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-red-400">
          <XCircle className="h-5 w-5" />
          Missing Skills
        </h2>
        <div className="flex flex-wrap gap-2">
          {data.missing_skills.map((skill) => (
            <span
              key={skill}
              className="rounded-full border border-red-800 bg-red-950/40 px-3 py-1.5 text-sm text-red-300"
            >
              {skill}
            </span>
          ))}
          {data.missing_skills.length === 0 && (
            <p className="text-gray-500">No gaps detected.</p>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-amber-400">
          <Lightbulb className="h-5 w-5" />
          Recommendations
        </h2>
        <ul className="space-y-3">
          {data.recommendations.map((rec, i) => (
            <li key={i} className="flex gap-3 text-gray-300">
              <TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-indigo-400" />
              {rec}
            </li>
          ))}
          {data.recommendations.length === 0 && (
            <p className="text-gray-500">No recommendations at this time.</p>
          )}
        </ul>
      </div>
    </div>
  );
}
