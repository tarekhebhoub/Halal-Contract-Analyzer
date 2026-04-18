const STYLES = {
  none: "bg-slate-100 text-slate-700",
  low: "bg-blue-100 text-blue-700",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-700",
};

export default function RiskBadge({ level }) {
  return <span className={`badge ${STYLES[level] || STYLES.none}`}>{level.toUpperCase()}</span>;
}
