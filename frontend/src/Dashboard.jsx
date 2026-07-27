import React, { useState, useEffect, useRef } from "react";
import API from "./api";
import Header from "./components/Header";
import HelpTooltip from "./components/HelpTooltip";
import Spinner from "./components/Spinner";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/dashboard.css";

const SOURCES = [
  {
    key: "semantic_scholar",
    labelKey: "dashboard.sourceSemanticScholar",
    helpKey: "dashboard.sourceSemanticScholarHelp",
    linkFor: (article) =>
      `https://www.semanticscholar.org/paper/${article.title.replace(/ /g, "-")}/${article.id}`,
  },
  {
    key: "clinical_trials",
    labelKey: "dashboard.sourceClinicalTrials",
    helpKey: "dashboard.sourceClinicalTrialsHelp",
    linkFor: (article) => `https://clinicaltrials.gov/search?cond=${article.id}`,
  },
  {
    key: "pubmed",
    labelKey: "dashboard.sourcePubmed",
    helpKey: "dashboard.sourcePubmedHelp",
    linkFor: (article) => `https://pubmed.ncbi.nlm.nih.gov/${article.id}/`,
  },
];

export default function Dashboard() {
  const { t } = useLanguage();
  const hasRun = useRef(false);
  const pollingInterval = useRef(null);  // <-- ligne manquante ajoutée
  const [results, setResults] = useState({
    semantic_scholar: [],
    clinical_trials: [],
    pubmed: []
  });
  const [loading, setLoading] = useState(true);
  const [noUpdate, setNoUpdate] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const token = localStorage.getItem("token");

    const fetchData = async () => {
      try {
        const response = await API.get("/dashboard-data", {
          headers: { Authorization: `Bearer ${token}` }
        });

        const categorized = {
          semantic_scholar: [],
          clinical_trials: [],
          pubmed: []
        };

        response.data.forEach((article) => {
          if (article.source === "Semantic Scholar") {
            categorized.semantic_scholar.push(article);
          } else if (article.source === "Clinical Trials") {
            categorized.clinical_trials.push(article);
          } else if (article.source === "PubMed") {
            categorized.pubmed.push(article);
          }
        });

        setResults(categorized);
        setNoUpdate(false);
        setLoading(false);

        if (pollingInterval.current) clearInterval(pollingInterval.current);
      } catch (err) {
        if (err.response?.status === 404) {
          setNoUpdate(true);
          setLoading(false);
          if (!pollingInterval.current) {
            pollingInterval.current = setInterval(fetchData, 15000);
          }
        } else {
          setError(err.response?.data?.detail || "Erreur lors du chargement");
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      if (pollingInterval.current) clearInterval(pollingInterval.current);
    };
  }, []);

  return (
    <>
      <Header />
      <div className="page">
        <h1>{t("dashboard.welcomeTitle")}</h1>

        {loading ? (
          <Spinner />
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : noUpdate ? (
          <p className="dashboard-empty">{t("dashboard.noUpdate")}</p>
        ) : (
          SOURCES.map((source) => (
            <section key={source.key} className="dashboard-section">
              <h3 className="dashboard-section__title">
                <span className="badge">{t(source.labelKey)}</span>
                <HelpTooltip text={t(source.helpKey)} />
              </h3>

              {results[source.key].length === 0 ? (
                <p className="dashboard-empty">{t("dashboard.noResults")}</p>
              ) : (
                <div className="article-list">
                  {results[source.key].map((article) => (
                    <article key={article.id} className="article-card">
                      <h4 className="article-card__title">{article.title}</h4>
                      <p className="article-card__abstract">{article.abstract}</p>
                      <a
                        className="article-card__link"
                        href={source.linkFor(article)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {t("common.readMore")}
                      </a>
                    </article>
                  ))}
                </div>
              )}
            </section>
          ))
        )}
      </div>
    </>
  );
}
