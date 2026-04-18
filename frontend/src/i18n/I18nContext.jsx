/**
 * Lightweight i18n: just an object map + a hook. No external dependency.
 * Persists choice in localStorage and toggles document <html dir/lang>.
 */
import { createContext, useContext, useEffect, useState, useCallback } from "react";

const STRINGS = {
  en: {
    "app.title": "Halal Contract Analyzer",
    "nav.dashboard": "Dashboard",
    "nav.logout": "Logout",
    "footer.disclaimer":
      "⚖️ This tool provides risk indicators based on Islamic finance principles and does not replace qualified scholarly judgment.",

    "auth.signin": "Sign in",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.signing_in": "Signing in…",
    "auth.no_account": "No account?",
    "auth.register": "Register",
    "auth.create_account": "Create your account",
    "auth.first_name": "First name",
    "auth.last_name": "Last name",
    "auth.password_hint": "Password (8+ chars)",
    "auth.organization": "Organization (optional)",
    "auth.creating": "Creating…",
    "auth.have_account": "Have an account?",
    "auth.invalid_credentials": "Invalid credentials",

    "dashboard.title": "Contracts",
    "dashboard.subtitle":
      "Upload a plain-text (.txt) contract to analyze it for potential Islamic-finance compliance risks.",
    "dashboard.dropzone.idle": "Drag & drop a contract, or click to choose a file",
    "dashboard.dropzone.active": "Drop your contract here",
    "dashboard.dropzone.uploading": "Analyzing…",
    "dashboard.dropzone.hint": "TXT only — max 15 MB",
    "dashboard.col.contract": "Contract",
    "dashboard.col.status": "Status",
    "dashboard.col.score": "Risk score",
    "dashboard.col.uploaded": "Uploaded",
    "dashboard.empty": "No contracts yet.",
    "dashboard.open": "Open →",

    "analysis.score": "Compliance risk score",
    "analysis.high": "High",
    "analysis.medium": "Medium",
    "analysis.low": "Low",
    "analysis.clauses": "Clauses",
    "analysis.clause": "Clause",
    "analysis.confidence": "conf.",
    "analysis.matched": "Matched:",
    "analysis.evidences": "View Quran / Sunnah references",
    "analysis.reanalyze": "Re-analyze",
    "analysis.reanalyze_arabic": "Re-analyze in Arabic",
    "analysis.reanalyze_english": "Re-analyze in English",
    "analysis.download_report": "Download PDF report",
    "analysis.processing_failed": "Processing failed:",
    "analysis.loading": "Loading…",
    "analysis.failed_to_load": "Failed to load contract",

    "lang.label": "Language",
    "lang.en": "English",
    "lang.ar": "العربية",
  },
  ar: {
    "app.title": "محلّل العقود الحلال",
    "nav.dashboard": "لوحة التحكم",
    "nav.logout": "تسجيل الخروج",
    "footer.disclaimer":
      "⚖️ توفّر هذه الأداة مؤشرات احتمالية للمخاطر بناءً على مبادئ التمويل الإسلامي ولا تُغني عن فتوى أهل العلم المختصّين.",

    "auth.signin": "تسجيل الدخول",
    "auth.email": "البريد الإلكتروني",
    "auth.password": "كلمة المرور",
    "auth.signing_in": "جاري تسجيل الدخول…",
    "auth.no_account": "ليس لديك حساب؟",
    "auth.register": "إنشاء حساب",
    "auth.create_account": "أنشئ حسابك",
    "auth.first_name": "الاسم الأول",
    "auth.last_name": "اسم العائلة",
    "auth.password_hint": "كلمة المرور (٨ أحرف فأكثر)",
    "auth.organization": "المؤسسة (اختياري)",
    "auth.creating": "جاري الإنشاء…",
    "auth.have_account": "لديك حساب بالفعل؟",
    "auth.invalid_credentials": "بيانات الاعتماد غير صحيحة",

    "dashboard.title": "العقود",
    "dashboard.subtitle":
      "ارفع عقدًا نصيًّا (.txt) لتحليله ورصد المخاطر المحتملة من منظور الامتثال للتمويل الإسلامي.",
    "dashboard.dropzone.idle": "اسحب وأفلت ملفًا، أو انقر لاختيار ملف",
    "dashboard.dropzone.active": "أفلت الملف هنا",
    "dashboard.dropzone.uploading": "جاري التحليل…",
    "dashboard.dropzone.hint": "ملفات TXT فقط — بحدّ أقصى ١٥ ميغابايت",
    "dashboard.col.contract": "العقد",
    "dashboard.col.status": "الحالة",
    "dashboard.col.score": "درجة المخاطرة",
    "dashboard.col.uploaded": "تاريخ الرفع",
    "dashboard.empty": "لا توجد عقود بعد.",
    "dashboard.open": "فتح ←",

    "analysis.score": "درجة مخاطر الامتثال",
    "analysis.high": "مرتفعة",
    "analysis.medium": "متوسطة",
    "analysis.low": "منخفضة",
    "analysis.clauses": "البنود",
    "analysis.clause": "البند",
    "analysis.confidence": "ثقة",
    "analysis.matched": "تطابقات:",
    "analysis.evidences": "عرض مراجع من القرآن والسنة",
    "analysis.reanalyze": "إعادة التحليل",
    "analysis.reanalyze_arabic": "إعادة التحليل بالعربية",
    "analysis.reanalyze_english": "إعادة التحليل بالإنجليزية",
    "analysis.download_report": "تنزيل التقرير PDF",
    "analysis.processing_failed": "فشل المعالجة:",
    "analysis.loading": "جاري التحميل…",
    "analysis.failed_to_load": "تعذّر تحميل العقد",

    "lang.label": "اللغة",
    "lang.en": "English",
    "lang.ar": "العربية",
  },
};

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [locale, setLocaleState] = useState(
    () => localStorage.getItem("locale") || "en"
  );

  const setLocale = useCallback((next) => {
    if (!STRINGS[next]) return;
    localStorage.setItem("locale", next);
    setLocaleState(next);
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
  }, [locale]);

  const t = useCallback(
    (key) => STRINGS[locale]?.[key] ?? STRINGS.en[key] ?? key,
    [locale]
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t, dir: locale === "ar" ? "rtl" : "ltr" }}>
      {children}
    </I18nContext.Provider>
  );
}

export const useI18n = () => useContext(I18nContext);
