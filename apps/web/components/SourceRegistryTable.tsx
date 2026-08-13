"use client";

import type { SourceEntry } from "@/lib/api";

const STATUS_STYLE: Record<string, string> = {
  ACTIVE: "badge-live",
  REGISTERED_NOT_INTEGRATED: "badge-pending",
  CANDIDATE_NOT_INTEGRATED: "badge-pending",
  RESTRICTED: "badge-restricted",
};

const STATUS_LABEL: Record<string, string> = {
  ACTIVE: "Active",
  REGISTERED_NOT_INTEGRATED: "Registered",
  CANDIDATE_NOT_INTEGRATED: "Candidate",
  RESTRICTED: "Restricted",
};

interface Props {
  sources: SourceEntry[];
}

export function SourceRegistryTable({ sources }: Props) {
  return (
    <div className="overflow-x-auto -mx-4 sm:mx-0">
      <table className="w-full text-xs min-w-[640px]" aria-label="Registered data sources">
        <thead>
          <tr className="border-b border-white/[0.06]">
            {["Source", "Domain", "Scope", "Access", "Status", "Records", "Last Ingest"].map(
              (h) => (
                <th
                  key={h}
                  className="text-left py-3 px-3 text-[10px] font-semibold text-gray-500 uppercase tracking-widest"
                >
                  {h}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody>
          {sources.map((src) => (
            <tr
              key={src.source_id}
              className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
            >
              <td className="py-3 px-3">
                <p className="text-white font-medium">{src.source_name}</p>
                <p className="text-gray-600 mt-0.5">{src.owner}</p>
              </td>
              <td className="py-3 px-3 text-gray-400">{src.domain}</td>
              <td className="py-3 px-3 text-gray-400">{src.geographic_scope}</td>
              <td className="py-3 px-3 text-gray-500">{src.access_method}</td>
              <td className="py-3 px-3">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide ${
                    STATUS_STYLE[src.integration_status] ?? "badge-pending"
                  }`}
                >
                  {STATUS_LABEL[src.integration_status] ?? src.integration_status}
                </span>
              </td>
              <td className="py-3 px-3 text-right tabular-nums">
                <span className="text-white">{(src.total_records_ingested || 0).toLocaleString()}</span>
              </td>
              <td className="py-3 px-3 text-gray-500">
                {src.last_ingested_at
                  ? new Date(src.last_ingested_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
