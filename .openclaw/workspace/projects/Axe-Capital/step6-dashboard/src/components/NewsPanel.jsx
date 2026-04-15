import { useEffect, useState } from "react";

function scoreColor(score) {
  if (score >= 9) return "bg-red-600 text-white";
  if (score >= 7) return "bg-orange-500 text-white";
  return "bg-yellow-400 text-black";
}

function relevanceChip(rel) {
  const colors = {
    held: "bg-blue-600 text-white",
    watchlist: "bg-blue-300 text-black",
    sector: "bg-gray-200 text-gray-800",
    none: "bg-gray-100 text-gray-500",
  };
  return colors[rel] || colors.none;
}

function NewsItem({ item }) {
  return (
    <article className="border-b border-gray-100 py-3">
      <div className="flex items-center gap-2 mb-1">
        <span className={`text-xs px-2 py-0.5 rounded ${scoreColor(item.impact_score)}`}>
          impact {item.impact_score}
        </span>
        <span className={`text-xs px-2 py-0.5 rounded ${relevanceChip(item.portfolio_relevance)}`}>
          {item.portfolio_relevance}
        </span>
        {item.tickers_mentioned?.map((t) => (
          <span key={t} className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">{t}</span>
        ))}
        <span className="ml-auto text-xs text-gray-500">{item.source} · {item.published_at}</span>
      </div>
      <a href={item.url} target="_blank" rel="noreferrer" className="font-semibold text-gray-900 hover:underline">
        {item.title}
      </a>
      <p className="text-sm text-gray-700 mt-1">{item.impact_rationale}</p>
      {item.decision_hook && (
        <p className="text-sm text-blue-700 mt-1">→ {item.decision_hook}</p>
      )}
    </article>
  );
}

export default function NewsPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/news-latest.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Hot News</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!data) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Hot News</h2><p className="text-gray-500">Loading…</p></section>;

  return (
    <section className="p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-xl font-bold">Hot News</h2>
        <span className="text-xs text-gray-500">{data.items_kept} kept of {data.items_in} · {data.generated_at}</span>
      </div>
      {data.items.length === 0 ? (
        <p className="text-gray-500 text-sm">No items cleared the impact threshold.</p>
      ) : (
        data.items.map((it) => <NewsItem key={it.id} item={it} />)
      )}
    </section>
  );
}
