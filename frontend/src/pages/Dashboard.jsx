import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import api from "../api/client.js";
import { useI18n } from "../i18n/I18nContext.jsx";

export default function Dashboard() {
  const { t, locale } = useI18n();
  const [contracts, setContracts] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    const { data } = await api.get("/contracts/");
    setContracts(data.results || data);
  };

  useEffect(() => { refresh(); }, []);

  const onDrop = useCallback(async (files) => {
    if (!files?.length) return;
    setUploading(true); setError("");
    try {
      const fd = new FormData();
      fd.append("file", files[0]);
      fd.append("title", files[0].name);
      fd.append("language", locale);
      await api.post("/contracts/upload/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await refresh();
    } catch (e) {
      setError(e.response?.data?.detail || JSON.stringify(e.response?.data) || "Upload failed");
    } finally { setUploading(false); }
  }, [locale]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: { "text/plain": [".txt"] },
    maxSize: 15 * 1024 * 1024,
  });

  return (
    <div className="mx-auto max-w-6xl px-6 py-8 space-y-8">
      <section>
        <h1 className="text-2xl font-bold">{t("dashboard.title")}</h1>
        <p className="text-slate-600 mt-1">{t("dashboard.subtitle")}</p>
      </section>

      <section
        {...getRootProps()}
        className={`card p-10 text-center cursor-pointer border-2 border-dashed
          ${isDragActive ? "border-brand-600 bg-brand-50" : "border-slate-300"}`}
      >
        <input {...getInputProps()} />
        <p className="font-medium">
          {uploading
            ? t("dashboard.dropzone.uploading")
            : isDragActive
            ? t("dashboard.dropzone.active")
            : t("dashboard.dropzone.idle")}
        </p>
        <p className="text-xs text-slate-500 mt-1">{t("dashboard.dropzone.hint")}</p>
        {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
      </section>

      <section className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="text-start px-4 py-3 font-medium">{t("dashboard.col.contract")}</th>
              <th className="text-start px-4 py-3 font-medium">{t("dashboard.col.status")}</th>
              <th className="text-start px-4 py-3 font-medium">{t("dashboard.col.score")}</th>
              <th className="text-start px-4 py-3 font-medium">{t("dashboard.col.uploaded")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {contracts.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                {t("dashboard.empty")}
              </td></tr>
            )}
            {contracts.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="px-4 py-3">{c.title}</td>
                <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                <td className="px-4 py-3">
                  {c.risk_score != null ? <RiskScore score={c.risk_score} /> : "—"}
                </td>
                <td className="px-4 py-3 text-slate-500">
                  {new Date(c.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-end">
                  <Link to={`/contracts/${c.id}`} className="text-brand-700 font-medium">
                    {t("dashboard.open")}
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function StatusBadge({ status }) {
  const colors = {
    pending: "bg-slate-100 text-slate-700",
    extracting: "bg-blue-100 text-blue-700",
    analyzing: "bg-amber-100 text-amber-700",
    completed: "bg-emerald-100 text-emerald-700",
    failed: "bg-red-100 text-red-700",
  };
  return <span className={`badge ${colors[status] || colors.pending}`}>{status}</span>;
}

function RiskScore({ score }) {
  const tone = score >= 70 ? "text-red-600" : score >= 40 ? "text-amber-600" : "text-emerald-600";
  return <span className={`font-semibold ${tone}`}>{score}/100</span>;
}
