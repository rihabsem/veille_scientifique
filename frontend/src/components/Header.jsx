import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import { useLanguage } from "../i18n/LanguageContext";
import { useTheme } from "../theme/ThemeContext";
import { SunIcon, MoonIcon, GlobeIcon, LogoutIcon } from "./icons";
import "./Header.css";

export default function Header({ userName }) {
  const { t, lang, toggleLang } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [fetchedName, setFetchedName] = useState(null);

  const isAuthenticated = Boolean(localStorage.getItem("token"));
  const selfFetch = userName === undefined;
  const name = selfFetch ? fetchedName : userName;

  useEffect(() => {
    if (!selfFetch || !isAuthenticated) return;

    let cancelled = false;
    API.get("/data")
      .then((res) => {
        if (!cancelled) setFetchedName(res.data?.nom ?? null);
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [selfFetch, isAuthenticated]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__logo" aria-hidden="true">VS</span>
        <span className="app-header__name">{t("common.appName")}</span>
      </div>

      <div className="app-header__actions">
        {isAuthenticated && name && (
          <span className="app-header__greeting">
            {t("header.greeting", { name })}
          </span>
        )}

        {isAuthenticated && (
          <a className="app-header__link" href="/user-data">
            {t("common.editInfo")}
          </a>
        )}

        <button
          type="button"
          className="icon-btn app-header__lang-btn"
          onClick={toggleLang}
          aria-label={t("header.langToggleLabel")}
          title={t("header.langToggleLabel")}
        >
          <GlobeIcon width={16} height={16} />
          <span className="app-header__lang-code">{lang.toUpperCase()}</span>
        </button>

        <button
          type="button"
          className="icon-btn"
          onClick={toggleTheme}
          aria-label={
            theme === "light"
              ? t("header.themeToggleLightLabel")
              : t("header.themeToggleDarkLabel")
          }
          title={
            theme === "light"
              ? t("header.themeToggleLightLabel")
              : t("header.themeToggleDarkLabel")
          }
        >
          {theme === "light" ? (
            <MoonIcon width={16} height={16} />
          ) : (
            <SunIcon width={16} height={16} />
          )}
        </button>

        {isAuthenticated && (
          <button
            type="button"
            className="btn btn-ghost app-header__logout"
            onClick={handleLogout}
          >
            <LogoutIcon width={16} height={16} />
            {t("common.logout")}
          </button>
        )}
      </div>
    </header>
  );
}
