import { useEffect, useState } from "react";

const AGENTS = ["axe_portfolio", "axe_alpha", "axe_news"];

function statusDot(status) {
  return {
    success: "bg-green-500",
    partial: "bg-yellow-500",
    failed: "bg-red-500",
    missing: "bg-gray-300",
  }[status] || "bg-gray-300";
}

function agentKey(agent) {
  return { axe_portfolio: "portfolio", axe_alpha: "alpha", axe_news: "news" }[agent] || agent;
}

function AgentRow({ agent, latest, health, onOpenTrace }) {
  const status = latest?.status || "missing";
  const duration = latest ? `${Math.round(latest.duration_ms / 1000)}s` : "—";
  const freshness = health?.artifacts?.[agentKey(agent)]?.status || "missing";
  const freshnessColor = {
    fresh: "text-green-700",
    stale: "text-yellow-700",
    missing: "text-red-700",
  }[freshness];
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100">
      <span className={`w-2 h-2 rounded-full ${statusDot(status)}`} />
      <span className="font-mono w-36 shrink-0">{agent}</span>
      <span className="text-xs text-gray-500 w-24">{status}</span>
      <span className="text-xs text-gray-500 w-16">{duration}</span>
      <span className={`text-xs ${freshnessColor} w-28`}>{freshness}</span>
      <span className="text-xs text-gray-600 truncate flex-1">{latest?.summary || "no runs yet"}</span>
      {latest && (
        <button
          onClick={() => onOpenTrace(latest.run_id)}
          className="text-xs text-blue-600 hover:underline"
        >
          view trace →
        </button>
      )}
    </div>
  );
}

export default function AgentStatusPanel({ onOpenTrace = () => {} }) {
  const [index, setIndex] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/traces/index.json").then((r) => (r.ok ? r.json() : { runs: [] })),
      fetch("/health.json").then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([idx, h]) => { setIndex(idx); setHealth(h); })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Status</h2><p className="text-red-600">Failed to load: {error}</p></section>;
  if (!index) return <section className="p-4"><h2 className="text-xl font-bold mb-2">Agent Status</h2><p className="text-gray-500">Loading…</p></section>;

  const latestByAgent = {};
  for (const run of index.runs) {
    if (!latestByAgent[run.agent]) latestByAgent[run.agent] = run;
  }

  return (
    <section className="p-4">
      <h2 className="text-xl font-bold mb-3">Agent Status</h2>
      {AGENTS.map((agent) => (
        <AgentRow
          key={agent}
          agent={agent}
          latest={latestByAgent[agent]}
          health={health}
          onOpenTrace={onOpenTrace}
        />
      ))}
      <div className="mt-4 text-xs text-gray-500">
        {index.runs.length} runs in index · {Object.keys(latestByAgent).length} agents tracked
      </div>
    </section>
  );
}
