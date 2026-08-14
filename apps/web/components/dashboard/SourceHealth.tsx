import { SourceEntry } from "@/lib/api";
import { Card, SectionLabel, EmptySection } from "../ui";

export function SourceHealth({ sources }: { sources: SourceEntry[] | null }) {
  return (
    <section aria-label="Data Sources" className="space-y-4">
      <SectionLabel>Data Sources & Health</SectionLabel>
      <Card>
        {!sources || sources.length === 0 ? (
          <EmptySection message="No sources registered." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sources.map(source => {
              const isHealthy = source.active_records > 0 || source.total_records_ingested > 0;
              const dateStr = source.last_ingested_at ? new Date(source.last_ingested_at).toLocaleString() : "Never";
              
              return (
                <div key={source.source_id} className="p-4 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium text-gray-200">{source.source_name}</span>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`} />
                      <span className="text-[10px] text-gray-500 uppercase">{isHealthy ? 'Healthy' : 'Unavailable'}</span>
                    </div>
                  </div>
                  <div className="space-y-1 text-xs text-gray-500">
                    <p>Last ingestion: {dateStr}</p>
                    <p>Active records: <span className="text-gray-300">{source.active_records}</span></p>
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
