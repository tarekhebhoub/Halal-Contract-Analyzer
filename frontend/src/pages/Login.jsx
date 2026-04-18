import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import { useI18n } from "../i18n/I18nContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const { t } = useI18n();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { await login(email, password); nav("/"); }
    catch (e) { setErr(e.response?.data?.detail || t("auth.invalid_credentials")); }
    finally { setBusy(false); }
  };

  return (
    <div className="mx-auto max-w-sm px-6 py-16">
      <h1 className="text-2xl font-bold mb-6">{t("auth.signin")}</h1>
      <form onSubmit={submit} className="space-y-4 card p-6">
        <input className="input ltr-only" placeholder={t("auth.email")} type="email"
          value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input ltr-only" placeholder={t("auth.password")} type="password"
          value={password} onChange={(e) => setPassword(e.target.value)} required />
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? t("auth.signing_in") : t("auth.signin")}
        </button>
        <p className="text-sm text-slate-600 text-center">
          {t("auth.no_account")} <Link to="/register" className="text-brand-700">{t("auth.register")}</Link>
        </p>
      </form>
    </div>
  );
}
