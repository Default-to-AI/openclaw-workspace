import { useEffect, useState } from "react";

function convictionColor(score) {
  if (score >= 8) return "bg-green-600 text-white";
  if (score >= 6) return "bg-yellow-500 text-black";
  return "bg-gray-400 text-white";
}

function OpportunityCard({ opp }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 rounded-lg p-4 mb-3 bg-white">
      <button
        className="w-full flex items-center justify-between text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-3">
          <span className="font-mono text-lg font-bold">{opp.ticker}</span>
          <span className="text-sm text-gray-600">{opp.opportunity_type}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${convictionColor(opp.conviction_score)}`}>
            conviction {opp.conviction_score}/10
          </span>
        </div>
        <span className="text-gray-400">{open ? "▾" : "▸"}</span>
      </button>
      <p className="mt-2 text-sm text-gray-800">{opp.thesis}</p>
      {open && (
        <div className="mt-3 space-y-2 text-sm">
          <div><span className="font-semibold">Trigger:</span> {opp.trigger_source} — {opp.trigger_data_point}</div>
          <div><span className="font-semibold">Why retail misses this:</span> {opp.why_retail_is_missing_this}</div>
          <div><span className="font-semibold">Risk flags:</span> {opp.risk_flags}</div>
          <details className="mt-2">
            <summary className="cursor-pointer text-gray-600">Raw facts</summary>
            <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(opp.raw_facts, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default function AlphaPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/alpha-latest.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Alpha Opportunities</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!data) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Alpha Opportunities</h2><p className="text-gray-500">Loading…</p></section>;

  const opps = data.top_opportunities || [];

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Alpha Opportunities</h2>
        <span className="text-xs text-gray-500">
          {opps.length} opportunities · {data.generated_at}
        </span>
      </div>
      {opps.length === 0 ? (
        <p className="text-gray-500">No opportunities in latest scan.</p>
      ) : (
        opps.map((opp) => <OpportunityCard key={opp.ticker} opp={opp} />)
      )}
    </section>
  );
}
