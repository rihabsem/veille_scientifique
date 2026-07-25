import { createContext, useContext, useEffect, useState } from "react";
import { translations } from "./translations";

const LanguageContext = createContext(null);

const STORAGE_KEY = "lang";
const DEFAULT_LANG = "fr";

function resolvePath(dict, path) {
  return path.split(".").reduce((acc, key) => (acc ? acc[key] : undefined), dict);
}

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "fr" || stored === "en" ? stored : DEFAULT_LANG;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
  }, [lang]);

  const toggleLang = () => setLang((prev) => (prev === "fr" ? "en" : "fr"));

  const t = (path, vars) => {
    const value = resolvePath(translations[lang], path);
    if (typeof value !== "string") return path;
    if (!vars) return value;
    return Object.keys(vars).reduce(
      (str, key) => str.replaceAll(`{${key}}`, vars[key]),
      value
    );
  };

  return (
    <LanguageContext.Provider value={{ lang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
