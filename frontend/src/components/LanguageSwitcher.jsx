import { useI18n } from "../i18n/I18nContext.jsx";

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <div className="inline-flex rounded-lg ring-1 ring-slate-200 bg-white overflow-hidden text-xs">
      {["en", "ar"].map((code) => (
        <button
          key={code}
          onClick={() => setLocale(code)}
          className={`px-3 py-1.5 font-medium transition ${
            locale === code
              ? "bg-brand-600 text-white"
              : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          {code === "en" ? "EN" : "ع"}
        </button>
      ))}
    </div>
  );
}
