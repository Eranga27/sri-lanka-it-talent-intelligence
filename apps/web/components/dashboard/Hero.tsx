import { MarketCoverage } from "@/lib/api";

export function Hero({ coverage }: { coverage: MarketCoverage | null }) {
  const isLive = coverage?.metrics?.data_available;
  const statusLabel = isLive ? "LIVE DATA" : "LIMITED COVERAGE";
  const statusColor = isLive ? "bg-emerald-500" : "bg-yellow-500";

  return (
    <section aria-labelledby="hero-heading" className="py-20 fade-up">
      <div className="max-w-4xl space-y-8">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/5 border border-white/10">
            <span className={`w-1.5 h-1.5 rounded-full ${statusColor} animate-pulse`} />
            <span className="text-[10px] font-medium text-gray-300 tracking-wider uppercase">
              {statusLabel}
            </span>
          </div>
        </div>
        
        <h1
          id="hero-heading"
          className="text-4xl sm:text-5xl lg:text-7xl font-light tracking-tight text-white leading-[1.1]"
        >
          Understanding where technology demand is emerging across the Sri Lankan employment market.
        </h1>
        
        <p className="text-lg text-gray-400 max-w-2xl font-light leading-relaxed">
          Sri Lanka IT Talent Intelligence is a deterministic data engine monitoring live technical skills and role vacancies.
        </p>
      </div>
    </section>
  );
}
