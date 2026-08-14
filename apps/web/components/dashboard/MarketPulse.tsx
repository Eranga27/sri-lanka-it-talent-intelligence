import { MarketSummary } from "@/lib/api";

export function MarketPulse({ summary }: { summary: MarketSummary | null }) {
  if (!summary?.data_available) return null;

  const date = summary.latest_ingestion ? new Date(summary.latest_ingestion) : new Date();
  const dateStr = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' });

  return (
    <div className="border-y border-white/10 py-12 flex flex-col items-center justify-center text-center fade-up">
      <h2 className="text-xs font-semibold text-gray-500 tracking-[0.2em] uppercase mb-6">Market Pulse</h2>
      <p className="text-4xl md:text-5xl font-light text-white tracking-tight mb-8">
        <span className="font-medium text-blue-400">{summary.total_sri_lankan_it_jobs || 0}</span> active IT roles observed
      </p>
      <div className="flex flex-col items-center gap-1 text-xs text-gray-500">
        <p>Updated: {dateStr} · {timeStr} UTC</p>
        <p className="italic opacity-70 mt-2">Historical comparison unavailable. Baseline is being established.</p>
      </div>
    </div>
  );
}
