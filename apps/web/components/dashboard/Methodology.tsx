import { SectionLabel } from "../ui";

export function Methodology() {
  return (
    <section aria-labelledby="methodology-heading" id="methodology" className="space-y-4">
      <SectionLabel>Methodology</SectionLabel>
      <div className="bg-[#111113] border border-white/5 rounded-xl p-8 transition-all duration-300 space-y-8 text-sm text-gray-400 leading-relaxed">
        
        <div>
          <h3 className="text-white font-medium mb-2">What is measured?</h3>
          <p>Observed job postings from connected public employment sources (Applicant Tracking Systems like Greenhouse, Workable, Lever). Data is fetched directly from public endpoints.</p>
        </div>

        <div>
          <h3 className="text-white font-medium mb-2">What is not measured?</h3>
          <p>The complete national employment market. This dashboard only visualizes data from currently connected integrations and explicitly ignores closed or untrackable recruitment channels.</p>
        </div>

        <div>
          <h3 className="text-white font-medium mb-2">How are skills identified?</h3>
          <p>Deterministic local extraction from job descriptions using a predefined taxonomy of over 40 canonical skills. Natural language processing relies on token boundaries and alias mapping to avoid false positives.</p>
        </div>

        <div>
          <h3 className="text-white font-medium mb-2">How are roles classified?</h3>
          <p>Weighted deterministic evidence from job titles, departments, descriptions, and detected skills (Keyword Match V2 methodology). Roles not meeting confidence thresholds remain unclassified.</p>
        </div>

        <div>
          <h3 className="text-white font-medium mb-2">Why is coverage limited?</h3>
          <p>Only a subset of verified public employment sources is currently connected in this early phase. The platform maintains strict adherence to a zero-cost architecture, deliberately avoiding paid scraping or proprietary datasets.</p>
        </div>

      </div>
    </section>
  );
}
