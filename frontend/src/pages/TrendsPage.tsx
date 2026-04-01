import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useTrends } from "../api/hooks";

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a78bfa",
  "#3b82f6",
  "#06b6d4",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#ec4899",
  "#14b8a6",
];

export default function TrendsPage() {
  const [period, setPeriod] = useState<"weekly" | "monthly">("weekly");
  const { data: trends, isLoading } = useTrends(period, 10);

  // Transform data: pivot from per-skill arrays to per-date rows
  const chartData = (() => {
    if (!trends || trends.length === 0) return [];

    const dateMap = new Map<string, Record<string, number>>();

    for (const skill of trends) {
      for (const point of skill.periods) {
        if (!dateMap.has(point.date)) {
          dateMap.set(point.date, { date: 0 } as unknown as Record<string, number>);
        }
        const row = dateMap.get(point.date)!;
        row[skill.skill_name] = point.count;
      }
    }

    return Array.from(dateMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, values]) => ({ date, ...values }));
  })();

  const skillNames = (trends ?? []).map((t) => t.skill_name);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Skill Trends</h1>
          <p className="mt-1 text-gray-400">
            Track how skill demand changes over time
          </p>
        </div>

        {/* Period toggle */}
        <div className="flex rounded-lg border border-gray-700 bg-gray-900">
          <button
            onClick={() => setPeriod("weekly")}
            className={`rounded-l-lg px-4 py-2 text-sm font-medium transition-colors ${
              period === "weekly"
                ? "bg-indigo-600 text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Weekly
          </button>
          <button
            onClick={() => setPeriod("monthly")}
            className={`rounded-r-lg px-4 py-2 text-sm font-medium transition-colors ${
              period === "monthly"
                ? "bg-indigo-600 text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Monthly
          </button>
        </div>
      </div>

      {/* Line chart */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Top 10 Skills Over Time
        </h2>
        {isLoading ? (
          <div className="flex h-96 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex h-96 items-center justify-center text-gray-500">
            No trend data available yet. Import job descriptions over time to
            see trends.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={{ stroke: "#4b5563" }}
              />
              <YAxis
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={{ stroke: "#4b5563" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f3f4f6",
                }}
              />
              <Legend
                wrapperStyle={{ color: "#d1d5db", paddingTop: "1rem" }}
              />
              {skillNames.map((name, i) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={COLORS[i % COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Raw data table */}
      {(trends ?? []).length > 0 && (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Raw Trend Data
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="px-4 py-3 font-medium text-gray-400">
                    Skill
                  </th>
                  {chartData.map((row) => (
                    <th
                      key={row.date}
                      className="px-4 py-3 font-medium text-gray-400"
                    >
                      {row.date}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {skillNames.map((name, i) => (
                  <tr
                    key={name}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30"
                  >
                    <td className="px-4 py-3 font-medium text-white">
                      <span className="flex items-center gap-2">
                        <span
                          className="inline-block h-3 w-3 rounded-full"
                          style={{
                            backgroundColor: COLORS[i % COLORS.length],
                          }}
                        />
                        {name}
                      </span>
                    </td>
                    {chartData.map((row) => (
                      <td
                        key={row.date}
                        className="px-4 py-3 text-gray-300"
                      >
                        {(row as Record<string, unknown>)[name] as number ?? 0}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
