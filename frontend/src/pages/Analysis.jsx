import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client.js";
import RiskBadge from "../components/RiskBadge.jsx";
import { useI18n } from "../i18n/I18nContext.jsx";

const RISK_BG = {
  high: "bg-red-50 border-s-4 border-red-500",
  medium: "bg-amber-50 border-s-4 border-amber-500",
  low: "bg-blue-50 border-s-4 border-blue-500",
  none: "bg-white border-s-4 border-slate-200",
};

export default function Analysis() {
  const { id } = useParams();
  const { t } = useI18n();
  const [contract, setContract] = useState(null);
  const [error, setError] = useState("");
  const [pollCount, setPollCount] = useState(0);

  const load = async () => {
    try {
      const { data } = await api.get(`/contracts/${id}/`);
      setContract(data);
    } catch (e) {
      setError(t("analysis.failed_to_load"));
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [id]);

  // Poll while analysis in progress
  useEffect(() => {
    if (!contract || ["completed", "failed"].includes(contract.status)) return;
    const t = setTimeout(() => { load(); setPollCount((n) => n + 1); }, 2000);
    return () => clearTimeout(t);
    // eslint-disable-next-line
  }, [contract, pollCount]);

  if (error) return <div className="p-10 text-red-600">{error}</div>;
  if (!contract) return <div className="p-10">{t("analysis.loading")}</div>;

  const downloadReport = async () => {
    const res = await api.get(`/contracts/${id}/report/`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url; a.download = `halal-report-${id}.pdf`;
    a.click(); URL.revokeObjectURL(url);
  };

  const reprocess = async (lang) => {
    await api.post(`/contracts/${id}/reprocess/`, lang ? { lang } : {});
    await load();
  };

  const otherLang = contract.language === "ar" ? "en" : "ar";

  return (
    <div className="mx-auto max-w-6xl px-6 py-8 space-y-6">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold">{contract.title}</h1>
          <p className="text-sm text-slate-500">
            {contract.mime_type} · {(contract.size_bytes / 1024).toFixed(1)} KB ·
            {" "}{t("dashboard.col.status")}: <span className="font-medium">{contract.status}</span> ·
            {" "}{t("lang.label")}: <span className="font-medium uppercase">{contract.language}</span>
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button className="btn-ghost" onClick={() => reprocess()}>{t("analysis.reanalyze")}</button>
          <button className="btn-ghost" onClick={() => reprocess(otherLang)}>
            {otherLang === "ar" ? t("analysis.reanalyze_arabic") : t("analysis.reanalyze_english")}
          </button>
          {contract.analysis && (
            <button className="btn-primary" onClick={downloadReport}>
              {t("analysis.download_report")}
            </button>
          )}
        </div>
      </header>

      {contract.status === "failed" && (
        <div className="card p-4 bg-red-50 text-red-700">
          {t("analysis.processing_failed")} {contract.error_message}
        </div>
      )}

      {contract.analysis && <ScoreCard a={contract.analysis} />}

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">
          {t("analysis.clauses")} ({contract.clauses?.length || 0})
        </h2>
        {(contract.clauses || []).map((c) => (
          <ClauseCard key={c.id} clause={c} />
        ))}
      </section>

      <p className="text-xs text-slate-500 italic">⚖️ {contract.disclaimer}</p>
    </div>
  );
}

function ScoreCard({ a }) {
  const { t } = useI18n();
  const tone = a.risk_score >= 70 ? "text-red-600"
    : a.risk_score >= 40 ? "text-amber-600" : "text-emerald-600";
  return (
    <section className="card p-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="text-sm text-slate-500">{t("analysis.score")}</p>
          <p className={`text-5xl font-bold ${tone}`}>
            {a.risk_score}<span className="text-lg text-slate-400">/100</span>
          </p>
        </div>
        <div className="grid grid-cols-3 gap-6 text-center">
          <Counter label={t("analysis.high")} value={a.high_risk_count} tone="text-red-600" />
          <Counter label={t("analysis.medium")} value={a.medium_risk_count} tone="text-amber-600" />
          <Counter label={t("analysis.low")} value={a.low_risk_count} tone="text-blue-600" />
        </div>
      </div>
      <p className="mt-4 text-slate-700 whitespace-pre-wrap">{a.summary}</p>
      {Object.keys(a.category_breakdown || {}).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          {Object.entries(a.category_breakdown).map(([k, v]) => (
            <span key={k} className="badge bg-slate-100 text-slate-700">{k}: {v}</span>
          ))}
        </div>
      )}
    </section>
  );
}

function Counter({ label, value, tone }) {
  return (
    <div>
      <p className={`text-2xl font-bold ${tone}`}>{value}</p>
      <p className="text-xs text-slate-500 uppercase tracking-wide">{label}</p>
    </div>
  );
}

function renderRichText(text) {
  // Lightweight markdown-ish renderer: bolds **x**, paragraphs on blank lines.
  if (!text) return null;
  const paragraphs = text.split(/\n{2,}/);
  return paragraphs.map((para, idx) => (
    <p key={idx} className="mb-2 last:mb-0 whitespace-pre-wrap leading-relaxed">
      {para.split(/(\*\*[^*]+\*\*)/g).map((chunk, i) =>
        chunk.startsWith("**") && chunk.endsWith("**")
          ? <strong key={i}>{chunk.slice(2, -2)}</strong>
          : chunk
      )}
    </p>
  ));
}

function ClauseCard({ clause }) {
  const { t } = useI18n();
  return (
    <div className={`card p-4 ${RISK_BG[clause.risk_level] || RISK_BG.none}`}>
      <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
        <span className="text-xs text-slate-500">
          {t("analysis.clause")} #{clause.position + 1}
        </span>
        <div className="flex items-center gap-2">
          {clause.category && (
            <span className="badge bg-slate-200 text-slate-700">{clause.category}</span>
          )}
          <RiskBadge level={clause.risk_level} />
          {clause.confidence > 0 && (
            <span className="text-xs text-slate-500">
              {clause.confidence}% {t("analysis.confidence")}
            </span>
          )}
        </div>
      </div>
      <p className="text-sm whitespace-pre-wrap">{clause.text}</p>

      {clause.matched_keywords?.length > 0 && (
        <p className="mt-2 text-xs text-slate-500">
          {t("analysis.matched")}{" "}
          {clause.matched_keywords.map((k) => (
            <span key={k} className="bg-yellow-100 px-1 mx-0.5 rounded">{k}</span>
          ))}
        </p>
      )}

      {clause.explanation && (
        <div className="mt-3 text-sm text-slate-700 bg-white/60 rounded-lg p-3 ring-1 ring-slate-200">
          {renderRichText(clause.explanation)}
        </div>
      )}

      {clause.evidences?.length > 0 && (
        <details className="mt-3">
          <summary className="text-xs text-brand-700 cursor-pointer">
            {t("analysis.evidences")} ({clause.evidences.length})
          </summary>
          <ul className="mt-2 space-y-2 text-xs text-slate-700">
            {clause.evidences.map((e, i) => (
              <li key={i} className="border-s-2 border-brand-500 ps-3">
                <p className="font-semibold">{e.source} — {e.reference}</p>
                <p className="italic">{e.text}</p>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
