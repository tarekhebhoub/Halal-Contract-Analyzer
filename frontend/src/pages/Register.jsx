import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import { useI18n } from "../i18n/I18nContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const { t, locale } = useI18n();
  const nav = useNavigate();
  const [form, setForm] = useState({
    email: "", password: "", first_name: "", last_name: "",
    organization: "", preferred_language: locale,
  });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { await register(form); nav("/"); }
    catch (e) {
      setErr(JSON.stringify(e.response?.data || "Registration failed"));
    } finally { setBusy(false); }
  };

  return (
    <div className="mx-auto max-w-md px-6 py-12">
      <h1 className="text-2xl font-bold mb-6">{t("auth.create_account")}</h1>
      <form onSubmit={submit} className="space-y-4 card p-6">
        <div className="grid grid-cols-2 gap-3">
          <input className="input" placeholder={t("auth.first_name")} value={form.first_name} onChange={upd("first_name")} />
          <input className="input" placeholder={t("auth.last_name")} value={form.last_name} onChange={upd("last_name")} />
        </div>
        <input className="input ltr-only" placeholder={t("auth.email")} type="email" required value={form.email} onChange={upd("email")} />
        <input className="input ltr-only" placeholder={t("auth.password_hint")} type="password" required value={form.password} onChange={upd("password")} />
        <input className="input" placeholder={t("auth.organization")} value={form.organization} onChange={upd("organization")} />
        <select className="input" value={form.preferred_language} onChange={upd("preferred_language")}>
          <option value="en">English</option>
          <option value="ar">العربية</option>
        </select>
        {err && <p className="text-red-600 text-sm break-words">{err}</p>}
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? t("auth.creating") : t("auth.create_account")}
        </button>
        <p className="text-sm text-slate-600 text-center">
          {t("auth.have_account")} <Link to="/login" className="text-brand-700">{t("auth.signin")}</Link>
        </p>
      </form>
    </div>
  );
}
