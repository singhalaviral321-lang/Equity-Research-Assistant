import { useState, useEffect } from "react";

// ── Mock data (replace with real API call to your n8n webhook) ─
const MOCK_DATA = {
  date: new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" }),
  summary: { strong_buys: 4, buys: 6, neutrals: 7, sells: 3 },
  all_results: [
    { ticker: "RELIANCE.NS",   name: "Reliance Industries",    sector: "Energy",        price: 2847.50, change_1d: 2.14,  composite_score: 81, signal: "STRONG BUY",  indicators: { rsi: 62.4, rsi_signal: "bullish",  macd_crossover: "bullish_crossover", volume_ratio: 1.8, obv_trend: "rising",  supertrend: "bullish", trend_strength: "strong"  }, reasons: ["MACD bullish crossover", "Volume 1.8x average — breakout conviction", "Above 50 & 200 DMA"], risks: [] },
    { ticker: "TCS.NS",        name: "Tata Consultancy",       sector: "IT",            price: 3921.00, change_1d: 1.42,  composite_score: 76, signal: "STRONG BUY",  indicators: { rsi: 58.1, rsi_signal: "bullish",  macd_crossover: "strengthening",    volume_ratio: 1.4, obv_trend: "rising",  supertrend: "bullish", trend_strength: "strong"  }, reasons: ["MACD strengthening", "OBV rising — accumulation pattern"], risks: [] },
    { ticker: "BAJFINANCE.NS", name: "Bajaj Finance",          sector: "Finance",       price: 7140.80, change_1d: 3.21,  composite_score: 74, signal: "STRONG BUY",  indicators: { rsi: 64.2, rsi_signal: "bullish",  macd_crossover: "bullish_crossover", volume_ratio: 2.1, obv_trend: "rising",  supertrend: "bullish", trend_strength: "very_strong" }, reasons: ["RSI healthy momentum", "Volume 2.1x — strong breakout"], risks: [] },
    { ticker: "HDFCBANK.NS",   name: "HDFC Bank",              sector: "Finance",       price: 1718.30, change_1d: 0.88,  composite_score: 72, signal: "STRONG BUY",  indicators: { rsi: 57.3, rsi_signal: "bullish",  macd_crossover: "strengthening",    volume_ratio: 1.3, obv_trend: "rising",  supertrend: "bullish", trend_strength: "strong"  }, reasons: ["Golden cross intact", "Analyst buy consensus"], risks: [] },
    { ticker: "INFY.NS",       name: "Infosys",                sector: "IT",            price: 1842.70, change_1d: 0.63,  composite_score: 68, signal: "BUY",         indicators: { rsi: 54.9, rsi_signal: "bullish",  macd_crossover: "strengthening",    volume_ratio: 1.1, obv_trend: "rising",  supertrend: "bullish", trend_strength: "moderate" }, reasons: ["MACD strengthening", "Price above 50 DMA"], risks: [] },
    { ticker: "IRCTC.NS",      name: "IRCTC",                  sector: "Travel",        price: 1020.45, change_1d: 1.92,  composite_score: 66, signal: "BUY",         indicators: { rsi: 61.2, rsi_signal: "bullish",  macd_crossover: "strengthening",    volume_ratio: 1.6, obv_trend: "rising",  supertrend: "bullish", trend_strength: "strong"  }, reasons: ["Volume spike on up day", "Near 52W high"], risks: [] },
    { ticker: "ZOMATO.NS",     name: "Zomato",                 sector: "Consumer",      price: 242.80,  change_1d: 2.44,  composite_score: 64, signal: "BUY",         indicators: { rsi: 60.4, rsi_signal: "bullish",  macd_crossover: "bullish_crossover", volume_ratio: 1.9, obv_trend: "rising",  supertrend: "bullish", trend_strength: "moderate" }, reasons: ["MACD crossover", "High volume"], risks: ["PE ratio elevated"] },
    { ticker: "MARUTI.NS",     name: "Maruti Suzuki",          sector: "Auto",          price: 12480.00,change_1d: 0.21,  composite_score: 58, signal: "BUY",         indicators: { rsi: 51.8, rsi_signal: "neutral",  macd_crossover: "strengthening",    volume_ratio: 0.9, obv_trend: "rising",  supertrend: "bullish", trend_strength: "moderate" }, reasons: ["Above all key MAs"], risks: ["Low volume"] },
    { ticker: "WIPRO.NS",      name: "Wipro",                  sector: "IT",            price: 548.20,  change_1d: -0.34, composite_score: 51, signal: "NEUTRAL",     indicators: { rsi: 48.2, rsi_signal: "neutral",  macd_crossover: "weakening",        volume_ratio: 0.8, obv_trend: "falling", supertrend: "bullish", trend_strength: "weak"    }, reasons: [], risks: ["MACD weakening"] },
    { ticker: "ICICIBANK.NS",  name: "ICICI Bank",             sector: "Finance",       price: 1248.70, change_1d: 0.14,  composite_score: 49, signal: "NEUTRAL",     indicators: { rsi: 50.1, rsi_signal: "neutral",  macd_crossover: "weakening",        volume_ratio: 0.7, obv_trend: "falling", supertrend: "neutral", trend_strength: "weak"    }, reasons: [], risks: [] },
    { ticker: "ADANIENT.NS",   name: "Adani Enterprises",      sector: "Conglomerate",  price: 2490.00, change_1d: -1.82, composite_score: 38, signal: "SELL",        indicators: { rsi: 41.2, rsi_signal: "bearish",  macd_crossover: "bearish_crossover", volume_ratio: 1.4, obv_trend: "falling", supertrend: "bearish", trend_strength: "moderate" }, reasons: [], risks: ["MACD bearish crossover", "High volume on red day", "Below 50 DMA"] },
    { ticker: "PAYTM.NS",      name: "Paytm (One97 Comm)",     sector: "Fintech",       price: 412.40,  change_1d: -3.21, composite_score: 28, signal: "SELL",        indicators: { rsi: 34.1, rsi_signal: "bearish",  macd_crossover: "bearish_crossover", volume_ratio: 2.2, obv_trend: "falling", supertrend: "bearish", trend_strength: "strong"  }, reasons: [], risks: ["RSI bearish", "MACD bearish crossover", "Heavy volume selling"] },
    { ticker: "POLICYBZR.NS",  name: "PB Fintech (PolicyBzr)", sector: "Fintech",       price: 1521.00, change_1d: -2.14, composite_score: 24, signal: "STRONG SELL", indicators: { rsi: 29.8, rsi_signal: "oversold",  macd_crossover: "bearish_crossover", volume_ratio: 1.8, obv_trend: "falling", supertrend: "bearish", trend_strength: "strong"  }, reasons: [], risks: ["RSI approaching oversold", "Consistent distribution", "Below all MAs"] },
  ]
};

// ── Color helpers ────────────────────────────────────────────
const SIGNAL_COLORS = {
  "STRONG BUY":  { bg: "bg-emerald-500/20", text: "text-emerald-400", border: "border-emerald-500/40", dot: "#10b981" },
  "BUY":         { bg: "bg-green-500/15",   text: "text-green-400",   border: "border-green-500/30",   dot: "#4ade80" },
  "NEUTRAL":     { bg: "bg-amber-500/15",   text: "text-amber-400",   border: "border-amber-500/30",   dot: "#fbbf24" },
  "SELL":        { bg: "bg-red-500/15",     text: "text-red-400",     border: "border-red-500/30",     dot: "#f87171" },
  "STRONG SELL": { bg: "bg-rose-600/20",    text: "text-rose-400",    border: "border-rose-600/40",    dot: "#fb7185" },
};

const getSignalColor = (signal) => SIGNAL_COLORS[signal] || SIGNAL_COLORS["NEUTRAL"];

const rsiColor = (rsi) =>
  rsi >= 70 ? "#ef4444" : rsi >= 55 ? "#10b981" : rsi >= 45 ? "#fbbf24" : rsi >= 30 ? "#f97316" : "#ef4444";

const ScoreBar = ({ value, color = "#10b981" }) => (
  <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
    <div
      className="h-full rounded-full transition-all duration-700"
      style={{ width: `${value}%`, background: color }}
    />
  </div>
);

const RSIGauge = ({ value }) => {
  const angle = ((value / 100) * 180) - 90;
  const color = rsiColor(value);
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="56" height="30" viewBox="0 0 56 30">
        <path d="M4 28 A24 24 0 0 1 52 28" fill="none" stroke="#ffffff10" strokeWidth="6" strokeLinecap="round"/>
        <path d="M4 28 A24 24 0 0 1 52 28" fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
          strokeDasharray="75.4" strokeDashoffset={75.4 * (1 - value/100)} />
        <line x1="28" y1="28" x2={28 + 18 * Math.cos((angle - 90) * Math.PI/180)}
              y2={28 + 18 * Math.sin((angle - 90) * Math.PI/180)}
              stroke={color} strokeWidth="2" strokeLinecap="round"/>
        <circle cx="28" cy="28" r="3" fill={color}/>
      </svg>
      <span className="text-xs font-bold" style={{ color }}>{value}</span>
    </div>
  );
};

const SignalBadge = ({ signal, compact }) => {
  const c = getSignalColor(signal);
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold border ${c.bg} ${c.text} ${c.border}`}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: c.dot }}/>
      {compact ? signal.replace("STRONG ", "S.") : signal}
    </span>
  );
};

// ── Indicator chip ───────────────────────────────────────────
const Chip = ({ label, value, positive }) => (
  <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium
    ${positive === true  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
      positive === false ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                           "bg-white/5 text-zinc-400 border border-white/10"}`}>
    {label}: <span className="font-bold">{value}</span>
  </span>
);

// ── Stock Row ────────────────────────────────────────────────
const StockRow = ({ stock, onClick, selected }) => {
  const sc = getSignalColor(stock.signal);
  const up = stock.change_1d >= 0;
  const ind = stock.indicators || {};
  return (
    <div
      onClick={() => onClick(stock)}
      className={`group relative px-4 py-3 cursor-pointer transition-all duration-200 border-b border-white/5
        hover:bg-white/5 ${selected ? "bg-white/8 border-l-2" : "border-l-2 border-l-transparent"}
      `}
      style={selected ? { borderLeftColor: sc.dot } : {}}
    >
      <div className="flex items-center gap-3">
        {/* Ticker + Name */}
        <div className="w-36 shrink-0">
          <div className="font-bold text-white text-sm leading-tight">{stock.ticker.replace(".NS","").replace(".BO","")}</div>
          <div className="text-xs text-zinc-500 truncate">{stock.name}</div>
        </div>

        {/* Signal */}
        <div className="w-28 shrink-0">
          <SignalBadge signal={stock.signal} compact />
        </div>

        {/* Score bar */}
        <div className="w-24 shrink-0">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-xs text-zinc-500">Score</span>
            <span className="text-xs font-bold" style={{ color: sc.dot }}>{stock.composite_score}</span>
          </div>
          <ScoreBar value={stock.composite_score} color={sc.dot} />
        </div>

        {/* Price + Change */}
        <div className="w-28 shrink-0 text-right">
          <div className="text-sm font-bold text-white">₹{stock.price.toLocaleString("en-IN")}</div>
          <div className={`text-xs font-semibold ${up ? "text-emerald-400" : "text-red-400"}`}>
            {up ? "▲" : "▼"} {Math.abs(stock.change_1d)}%
          </div>
        </div>

        {/* RSI Gauge */}
        <div className="w-14 shrink-0 flex justify-center">
          <RSIGauge value={ind.rsi || 50} />
        </div>

        {/* Quick chips */}
        <div className="hidden lg:flex flex-wrap gap-1 flex-1">
          <Chip label="MACD" value={ind.macd_crossover?.replace("_"," ").replace("crossover","↑")?.replace("bullish ↑","✓ bull")?.replace("bearish ↑","✗ bear") || "—"}
            positive={ind.macd_crossover?.includes("bullish") ? true : ind.macd_crossover?.includes("bearish") ? false : null}/>
          <Chip label="Vol" value={`${ind.volume_ratio}x`} positive={ind.volume_ratio > 1.3 && stock.change_1d > 0 ? true : ind.volume_ratio > 1.3 && stock.change_1d < 0 ? false : null}/>
          <Chip label="Trend" value={ind.trend_strength || "—"} positive={["strong","very_strong"].includes(ind.trend_strength) ? (stock.change_1d > 0) : null}/>
        </div>
      </div>
    </div>
  );
};

// ── Detail Panel ─────────────────────────────────────────────
const DetailPanel = ({ stock, onClose }) => {
  if (!stock) return null;
  const sc  = getSignalColor(stock.signal);
  const ind = stock.indicators || {};
  const up  = stock.change_1d >= 0;

  const indicatorRows = [
    { label: "RSI (14)",        value: ind.rsi,               note: ind.rsi_signal,                color: rsiColor(ind.rsi) },
    { label: "MACD Crossover",  value: ind.macd_crossover?.replace(/_/g," "), note: "",            color: ind.macd_crossover?.includes("bullish") ? "#10b981" : "#ef4444" },
    { label: "SuperTrend",      value: ind.supertrend,        note: "",                             color: ind.supertrend === "bullish" ? "#10b981" : "#ef4444" },
    { label: "Volume Ratio",    value: `${ind.volume_ratio}x`, note: ind.volume_ratio>1.5?"spike":"normal", color: ind.volume_ratio>1.5?"#f59e0b":"#94a3b8" },
    { label: "OBV Trend",       value: ind.obv_trend,         note: "",                             color: ind.obv_trend === "rising" ? "#10b981" : "#ef4444" },
    { label: "Trend Strength",  value: ind.trend_strength,    note: `ADX`,                          color: ["strong","very_strong"].includes(ind.trend_strength) ? "#f59e0b" : "#94a3b8" },
  ];

  return (
    <div className="h-full flex flex-col bg-zinc-900 border-l border-white/10">
      {/* Header */}
      <div className="p-5 border-b border-white/10" style={{ background: `${sc.dot}10` }}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl font-black text-white tracking-tight">
                {stock.ticker.replace(".NS","").replace(".BO","")}
              </span>
              <SignalBadge signal={stock.signal} />
            </div>
            <div className="text-sm text-zinc-400">{stock.name}</div>
            <div className="text-xs text-zinc-600 mt-0.5">{stock.sector}</div>
          </div>
          <button onClick={onClose} className="text-zinc-600 hover:text-white text-xl leading-none p-1">×</button>
        </div>

        <div className="flex items-end gap-4 mt-4">
          <div>
            <div className="text-3xl font-black text-white">₹{stock.price.toLocaleString("en-IN")}</div>
            <div className={`text-sm font-bold ${up ? "text-emerald-400" : "text-red-400"}`}>
              {up ? "▲" : "▼"} {Math.abs(stock.change_1d)}% today
            </div>
          </div>
          <div className="ml-auto text-right">
            <div className="text-xs text-zinc-600 mb-1">Composite Score</div>
            <div className="text-4xl font-black" style={{ color: sc.dot }}>{stock.composite_score}</div>
            <div className="text-xs" style={{ color: sc.dot }}>/100</div>
          </div>
        </div>
      </div>

      {/* Indicators */}
      <div className="p-4 border-b border-white/10 flex-1 overflow-y-auto">
        <div className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-3">Indicators</div>
        <div className="space-y-2.5">
          {indicatorRows.map(row => (
            <div key={row.label} className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">{row.label}</span>
              <div className="flex items-center gap-2">
                {row.note && <span className="text-xs text-zinc-600">{row.note}</span>}
                <span className="text-xs font-bold capitalize" style={{ color: row.color }}>{String(row.value)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Reasons */}
        {stock.reasons?.length > 0 && (
          <div className="mt-4">
            <div className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-2">Bullish Signals</div>
            {stock.reasons.map((r, i) => (
              <div key={i} className="flex items-start gap-2 mb-1.5">
                <span className="text-emerald-400 text-xs mt-0.5">✓</span>
                <span className="text-xs text-zinc-300">{r}</span>
              </div>
            ))}
          </div>
        )}

        {/* Risks */}
        {stock.risks?.length > 0 && (
          <div className="mt-4">
            <div className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-2">Risk Factors</div>
            {stock.risks.map((r, i) => (
              <div key={i} className="flex items-start gap-2 mb-1.5">
                <span className="text-red-400 text-xs mt-0.5">⚡</span>
                <span className="text-xs text-zinc-400">{r}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ── Summary card ────────────────────────────────────────────
const SummaryCard = ({ label, count, color, pct, onClick, active }) => (
  <div
    onClick={onClick}
    className={`relative flex-1 p-4 rounded-xl border cursor-pointer transition-all
      ${active ? "border-opacity-60 scale-[1.02]" : "border-opacity-20 hover:border-opacity-40"}`}
    style={{ borderColor: color, background: `${color}10` }}
  >
    <div className="text-3xl font-black" style={{ color }}>{count}</div>
    <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
    <div className="mt-2">
      <ScoreBar value={pct} color={color} />
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════
// MAIN DASHBOARD
// ═══════════════════════════════════════════════════════════════
export default function EquityDashboard() {
  const [data]        = useState(MOCK_DATA);
  const [filter, setFilter] = useState("ALL");
  const [selected, setSelected]   = useState(null);
  const [search, setSearch]       = useState("");
  const [sort, setSort]           = useState("score");
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const total = data.all_results.length;
  const { strong_buys, buys, neutrals, sells } = data.summary;

  const filters = [
    { key: "ALL",         label: "All",          color: "#94a3b8" },
    { key: "STRONG BUY",  label: "Strong Buy",   color: "#10b981" },
    { key: "BUY",         label: "Buy",          color: "#4ade80" },
    { key: "NEUTRAL",     label: "Neutral",      color: "#fbbf24" },
    { key: "SELL",        label: "Sell / Avoid", color: "#ef4444" },
  ];

  const filtered = data.all_results
    .filter(r => filter === "ALL" || r.signal === filter || (filter === "SELL" && r.signal === "STRONG SELL"))
    .filter(r => !search || r.ticker.toLowerCase().includes(search.toLowerCase()) || r.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sort === "score" ? b.composite_score - a.composite_score : sort === "change" ? b.change_1d - a.change_1d : a.ticker.localeCompare(b.ticker));

  return (
    <div className="min-h-screen bg-zinc-950 text-white font-mono" style={{ fontFamily: "'DM Mono', 'Fira Code', monospace" }}>
      {/* TOP NAV */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-zinc-900/80 backdrop-blur sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-black text-sm">ER</div>
          <span className="font-bold text-white text-sm tracking-tight">EQUITY RESEARCH ASSISTANT</span>
          <span className="text-zinc-600 text-xs hidden sm:block">/ Daily Briefing</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-600 hidden md:block">{data.date}</span>
          <button
            onClick={() => setLastRefresh(new Date())}
            className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-400 hover:text-white transition-colors"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* MAIN LAYOUT */}
      <div className="flex h-[calc(100vh-49px)]">
        {/* LEFT PANEL */}
        <div className={`flex flex-col flex-1 overflow-hidden ${selected ? "hidden md:flex" : "flex"}`}>

          {/* SUMMARY CARDS */}
          <div className="p-4 border-b border-white/10 bg-zinc-900/50">
            <div className="flex gap-3">
              <SummaryCard label="Strong Buy" count={strong_buys} color="#10b981" pct={strong_buys/total*100}
                onClick={() => setFilter(f => f === "STRONG BUY" ? "ALL" : "STRONG BUY")} active={filter === "STRONG BUY"} />
              <SummaryCard label="Buy" count={buys} color="#4ade80" pct={buys/total*100}
                onClick={() => setFilter(f => f === "BUY" ? "ALL" : "BUY")} active={filter === "BUY"} />
              <SummaryCard label="Neutral" count={neutrals} color="#fbbf24" pct={neutrals/total*100}
                onClick={() => setFilter(f => f === "NEUTRAL" ? "ALL" : "NEUTRAL")} active={filter === "NEUTRAL"} />
              <SummaryCard label="Sell / Avoid" count={sells} color="#ef4444" pct={sells/total*100}
                onClick={() => setFilter(f => f === "SELL" ? "ALL" : "SELL")} active={filter === "SELL"} />
            </div>
          </div>

          {/* TOOLBAR */}
          <div className="flex items-center gap-3 px-4 py-2.5 border-b border-white/10 bg-zinc-900/30">
            <input
              type="text"
              placeholder="Search ticker or name…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50"
            />
            <div className="flex items-center gap-1">
              {["score","change","name"].map(s => (
                <button key={s} onClick={() => setSort(s)}
                  className={`text-xs px-2.5 py-1.5 rounded-lg border transition-colors
                    ${sort === s ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400" : "bg-white/5 border-white/10 text-zinc-500 hover:text-white"}`}>
                  {s === "score" ? "Score ↓" : s === "change" ? "1D% ↓" : "A–Z"}
                </button>
              ))}
            </div>
            <div className="text-xs text-zinc-600">{filtered.length} stocks</div>
          </div>

          {/* TABLE HEADER */}
          <div className="flex items-center gap-3 px-4 py-2 bg-zinc-900/80 border-b border-white/5">
            <div className="w-36 text-xs text-zinc-600 uppercase tracking-wider">Stock</div>
            <div className="w-28 text-xs text-zinc-600 uppercase tracking-wider">Signal</div>
            <div className="w-24 text-xs text-zinc-600 uppercase tracking-wider">Score</div>
            <div className="w-28 text-xs text-zinc-600 uppercase tracking-wider text-right">Price</div>
            <div className="w-14 text-xs text-zinc-600 uppercase tracking-wider text-center">RSI</div>
            <div className="hidden lg:block flex-1 text-xs text-zinc-600 uppercase tracking-wider">Indicators</div>
          </div>

          {/* STOCK LIST */}
          <div className="flex-1 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-zinc-600 text-sm">
                No stocks match your filter
              </div>
            ) : (
              filtered.map(stock => (
                <StockRow
                  key={stock.ticker}
                  stock={stock}
                  selected={selected?.ticker === stock.ticker}
                  onClick={setSelected}
                />
              ))
            )}
          </div>

          {/* FOOTER */}
          <div className="px-4 py-2 border-t border-white/5 bg-zinc-900/50 flex items-center justify-between">
            <span className="text-xs text-zinc-700">Data: Yahoo Finance · Indicators: RSI, MACD, BB, ADX, OBV, SuperTrend +more</span>
            <span className="text-xs text-zinc-700">Refreshed {lastRefresh.toLocaleTimeString()}</span>
          </div>
        </div>

        {/* RIGHT PANEL — Detail */}
        {selected && (
          <div className="w-full md:w-80 lg:w-96 shrink-0 overflow-y-auto">
            <DetailPanel stock={selected} onClose={() => setSelected(null)} />
          </div>
        )}
      </div>
    </div>
  );
}
