"use client";

/**
 * DataFreshnessTag — shows how long ago data was last ingested.
 * Reads from a server-provided ISO timestamp string.
 */
interface Props {
  lastIngestedAt: string | null;
  source?: string;
}

export function DataFreshnessTag({ lastIngestedAt, source }: Props) {
  if (!lastIngestedAt) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs text-gray-500 badge-pending px-2 py-0.5 rounded-full">
        <span className="w-1.5 h-1.5 rounded-full bg-gray-500" />
        NO DATA
      </span>
    );
  }

  const date = new Date(lastIngestedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  let label: string;
  let freshness: "live" | "recent" | "stale";

  if (diffMins < 60) {
    label = diffMins < 2 ? "Just now" : `${diffMins}m ago`;
    freshness = "live";
  } else if (diffHours < 24) {
    label = `${diffHours}h ago`;
    freshness = "recent";
  } else if (diffDays < 7) {
    label = `${diffDays}d ago`;
    freshness = "stale";
  } else {
    label = date.toLocaleDateString();
    freshness = "stale";
  }

  const colorMap = {
    live:   "badge-live",
    recent: "badge-pending",
    stale:  "badge-restricted",
  };

  const dotMap = {
    live:   "bg-green-400 animate-pulse",
    recent: "bg-yellow-400",
    stale:  "bg-red-400",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-1 rounded-full ${colorMap[freshness]}`}
      title={`Last ingested: ${date.toLocaleString()}${source ? ` — Source: ${source}` : ""}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotMap[freshness]}`} />
      Updated {label}
      {source && <span className="opacity-60 ml-0.5">· {source}</span>}
    </span>
  );
}
