import { Link, NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth/AuthContext.jsx";
import { useI18n } from "./i18n/I18nContext.jsx";
import LanguageSwitcher from "./components/LanguageSwitcher.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Analysis from "./pages/Analysis.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const { t } = useI18n();
  if (loading) return <div className="p-10">{t("analysis.loading")}</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Shell({ children }) {
  const { user, logout } = useAuth();
  const { t } = useI18n();
  const nav = useNavigate();
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm ring-1 ring-slate-200">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-3 gap-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-brand-700">
            <span className="text-xl">☪</span> {t("app.title")}
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            <LanguageSwitcher />
            {user && (
              <>
                <NavLink to="/" className="text-slate-600 hover:text-slate-900">
                  {t("nav.dashboard")}
                </NavLink>
                <span className="text-slate-400 hidden sm:inline">{user.email}</span>
                <button className="btn-ghost" onClick={() => { logout(); nav("/login"); }}>
                  {t("nav.logout")}
                </button>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="bg-white border-t text-xs text-slate-500 py-3 text-center px-4">
        {t("footer.disclaimer")}
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/contracts/:id" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
