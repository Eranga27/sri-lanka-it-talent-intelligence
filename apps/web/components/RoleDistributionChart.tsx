"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import type { RoleDistributionEntry } from "@/lib/api";

const COLORS = [
  "#3b82f6", "#6366f1", "#8b5cf6", "#a78bfa",
  "#06b6d4", "#10b981", "#f59e0b", "#f87171",
];

const CustomTooltip = ({
  active, payload,
}: {
  active?: boolean;
  payload?: { value: number; name: string }[];
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs">
      <p className="text-white font-medium">{payload[0].name}</p>
      <p className="text-blue-400 font-semibold mt-0.5">{payload[0].value} jobs</p>
    </div>
  );
};

interface Props {
  data: RoleDistributionEntry[];
}

export function RoleDistributionChart({ data }: Props) {
  // Filter out nulls and "Unclassified" for the chart display, keep for table
  const chartData = data
    .filter((d) => d.role_category && d.role_category !== "Unclassified")
    .map((d) => ({ name: d.role_category!, count: d.job_count }));

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-gray-600 text-sm tracking-widest uppercase">No classified roles yet</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 0, right: 16, left: 0, bottom: 0 }}
      >
        <XAxis
          type="number"
          tick={{ fill: "#6b7280", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={180}
          tick={{ fill: "#9ca3af", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(59,130,246,0.06)" }} />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={20}>
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
