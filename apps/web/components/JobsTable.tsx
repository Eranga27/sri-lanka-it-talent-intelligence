"use client";

import type { JobRecord } from "@/lib/api";

interface Props {
  jobs: JobRecord[];
}

export function JobsTable({ jobs }: Props) {
  if (!jobs.length) {
    return (
      <div className="py-12 text-center">
        <p className="text-gray-600 text-sm">No job records available yet.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto -mx-4 sm:mx-0">
      <table className="w-full text-xs min-w-[720px]" aria-label="Live job postings">
        <thead>
          <tr className="border-b border-white/[0.06]">
            {["Title", "Company", "Location", "Role Category", "Status", "First Seen"].map(
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
          {jobs.map((job) => (
            <tr
              key={job.job_id}
              className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
            >
              <td className="py-3 px-3">
                {job.application_url ? (
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                  >
                    {job.title}
                  </a>
                ) : (
                  <span className="text-white font-medium">{job.title}</span>
                )}
              </td>
              <td className="py-3 px-3 text-gray-400">{job.company ?? "—"}</td>
              <td className="py-3 px-3 text-gray-500 max-w-[160px] truncate">
                {job.location ?? "—"}
                {job.country === "Sri Lanka" && (
                  <span className="ml-1 text-[9px] badge-live px-1.5 py-0.5 rounded-full">LK</span>
                )}
              </td>
              <td className="py-3 px-3">
                {job.role_category ? (
                  <span className="text-indigo-300">{job.role_category}</span>
                ) : (
                  <span className="text-gray-600 italic">Unclassified</span>
                )}
              </td>
              <td className="py-3 px-3">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-semibold ${
                    job.status === "active" ? "badge-live" : "badge-pending"
                  }`}
                >
                  {job.status}
                </span>
              </td>
              <td className="py-3 px-3 text-gray-500 tabular-nums">
                {new Date(job.first_seen_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
