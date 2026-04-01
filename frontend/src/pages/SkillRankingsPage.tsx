import { useState, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ArrowUpDown, Filter } from "lucide-react";
import { useSkillRankings } from "@/api/hooks";

type SortField = "name" | "frequency" | "percentage" | "category";
type SortDir = "asc" | "desc";

export default function SkillRankingsPage() {
  const [category, setCategory] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>("frequency");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const { data, isLoading } = useSkillRankings(category || undefined);
  const skills = data?.skills ?? [];

  const categories = useMemo(() => {
    const cats = new Set(skills.map((s) => s.category));
    return Array.from(cats).sort();
  }, [skills]);

  const sorted = useMemo(() => {
    return [...skills].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      return sortDir === "asc"
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });
  }, [skills, sortField, sortDir]);

  function toggleSort(field: SortField) {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  }

  const chartData = sorted.slice(0, 20);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Skill Rankings</h1>
          <p className="mt-1 text-gray-400">
            All skills extracted from job listings, ranked by frequency
          </p>
        </div>

        {/* Category filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-200 outline-none focus:border-indigo-500"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Top 20 Skills
        </h2>
        {isLoading ? (
          <div className="flex h-80 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="name"
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                axisLine={{ stroke: "#4b5563" }}
                angle={-45}
                textAnchor="end"
                height={80}
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
              <Bar
                dataKey="frequency"
                fill="#818cf8"
                radius={[6, 6, 0, 0]}
                name="Frequency"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-800 bg-gray-900">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              {(
                [
                  ["name", "Skill"],
                  ["category", "Category"],
                  ["frequency", "Frequency"],
                  ["percentage", "% of Jobs"],
                ] as const
              ).map(([field, label]) => (
                <th
                  key={field}
                  className="cursor-pointer px-5 py-3.5 font-medium text-gray-400 hover:text-gray-200"
                  onClick={() => toggleSort(field)}
                >
                  <span className="flex items-center gap-1.5">
                    {label}
                    <ArrowUpDown className="h-3.5 w-3.5" />
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((skill) => (
              <tr
                key={skill.id}
                className="border-b border-gray-800/50 transition-colors hover:bg-gray-800/40"
              >
                <td className="px-5 py-3 font-medium text-white">
                  {skill.name}
                </td>
                <td className="px-5 py-3">
                  <span className="rounded-full bg-gray-800 px-2.5 py-1 text-xs text-gray-300">
                    {skill.category}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-300">{skill.frequency}</td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-24 overflow-hidden rounded-full bg-gray-800">
                      <div
                        className="h-full rounded-full bg-indigo-500"
                        style={{ width: `${Math.min(skill.percentage, 100)}%` }}
                      />
                    </div>
                    <span className="text-gray-300">
                      {skill.percentage.toFixed(1)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {sorted.length === 0 && !isLoading && (
          <p className="px-5 py-10 text-center text-gray-500">
            No skills found. Import some job listings first.
          </p>
        )}
      </div>
    </div>
  );
}
