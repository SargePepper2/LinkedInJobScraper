import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, Briefcase, Layers, Target } from "lucide-react";
import { useSkillRankings, useSummary } from "../api/hooks";

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="mt-1 text-2xl font-bold text-white">{value}</p>
        </div>
        <div className={`rounded-lg p-3 ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: rankings, isLoading } = useSkillRankings();
  const { data: summary } = useSummary();

  const topSkills = (rankings ?? []).slice(0, 10);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="mt-1 text-gray-400">
          Overview of the job skills landscape
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Jobs"
          value={summary?.total_jobs ?? "--"}
          icon={Briefcase}
          color="bg-indigo-600"
        />
        <StatCard
          label="Total Skills"
          value={summary?.total_skills ?? "--"}
          icon={Layers}
          color="bg-purple-600"
        />
        <StatCard
          label="Top Category"
          value={summary?.top_category ?? "--"}
          icon={TrendingUp}
          color="bg-blue-600"
        />
        <StatCard
          label="Sources"
          value={summary?.sources?.length ?? "--"}
          icon={Target}
          color="bg-emerald-600"
        />
      </div>

      {/* Top 10 skills chart */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Top 10 In-Demand Skills
        </h2>
        {isLoading ? (
          <div className="flex h-80 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          </div>
        ) : topSkills.length === 0 ? (
          <div className="flex h-80 items-center justify-center text-gray-500">
            No data yet. Import some job descriptions to get started.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={360}>
            <BarChart
              data={topSkills}
              layout="vertical"
              margin={{ top: 0, right: 30, left: 100, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#374151"
                horizontal={false}
              />
              <XAxis
                type="number"
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={{ stroke: "#4b5563" }}
              />
              <YAxis
                dataKey="name"
                type="category"
                tick={{ fill: "#d1d5db", fontSize: 13 }}
                axisLine={false}
                tickLine={false}
                width={90}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f3f4f6",
                }}
              />
              <Bar
                dataKey="count"
                fill="#6366f1"
                radius={[0, 6, 6, 0]}
                name="Job Mentions"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
