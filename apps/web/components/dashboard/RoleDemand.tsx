import { RoleDemandEntry } from "@/lib/api";
import { Card, SectionLabel, EmptySection } from "../ui";

export function RoleDemand({ roles }: { roles: RoleDemandEntry[] | null }) {
  return (
    <section aria-labelledby="roles-heading" id="roles" className="space-y-4">
      <SectionLabel>Role Demand</SectionLabel>
      <p className="text-xs text-gray-600">
        Active Sri Lankan IT vacancies · keyword_match_v2
      </p>
      <Card>
        {!roles || roles.length === 0 ? (
          <EmptySection message="No role demand data yet. Run the pipeline to populate." />
        ) : (
          <div className="space-y-5" role="list" aria-label="IT role demand ranking">
            {roles.map((r, i) => {
              const pct = Math.min(r.job_percentage ?? 0, 100);
              return (
                <div key={r.role_category} role="listitem" className="group">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-200 font-medium">
                      {r.role_category}
                    </span>
                    <div className="flex items-center gap-3 tabular-nums">
                      <span className="text-white font-medium">{r.job_count}</span>
                      <span className="text-gray-500 text-[11px] w-10 text-right">
                        {pct.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  {/* CSS-animated bar */}
                  <div
                    className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden"
                    aria-label={`${r.role_category}: ${r.job_count} jobs`}
                  >
                    <div
                      className="h-full bg-blue-500 rounded-full bar-grow"
                      style={
                        {
                          "--bar-pct": `${pct}%`,
                          animationDelay: `${i * 60}ms`,
                        } as React.CSSProperties
                      }
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </section>
  );
}
