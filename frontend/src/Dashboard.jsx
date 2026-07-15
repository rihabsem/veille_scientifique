import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";

export default function Dashboard() {
  const navigate = useNavigate();
  const hasRun = useRef(false);
  const [results, setResults] = useState({
    semantic_scholar: [],
    clinical_trials: [],
    pubmed: []
  });
  const [loading, setLoading] = useState(true);
  const [noUpdate, setNoUpdate] = useState(false);
  const [error, setError] = useState(null);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const fetchData = async () => {
      const token = localStorage.getItem("token");
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
      } catch (err) {
        if (err.response?.status === 404) {
          setNoUpdate(true);
        } else {
          setError(err.response?.data?.detail || "Erreur lors du chargement");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Chargement...</p>;
  if (error) return <p>Erreur: {error}</p>;

  return (
    <div>
      <h1>Bienvenue !</h1>

      {noUpdate ? (
        <p>Pas de mise à jour nécessaire pour le moment.</p>
      ) : (
        <>
          <h3>Semantic Scholar</h3>
          <ul>
            {results.semantic_scholar.length === 0 && <li>Aucun résultat</li>}
            {results.semantic_scholar.map((article) => (
              <li key={article.id}>
                <strong>{article.title} - <a className="lien" href={`https://www.semanticscholar.org/paper/${article.title.replace(/ /g,"-")}/${article.id}`} target="_blank">pour consulter l'article</a></strong>
                <p>{article.abstract}</p>
              </li>
            ))}
          </ul>

          <h3>Clinical Trials</h3>
          <ul>
            {results.clinical_trials.length === 0 && <li>Aucun résultat</li>}
            {results.clinical_trials.map((article) => (
              <li key={article.id}>
                <strong>{article.title} - <a className="lien" href={`https://clinicaltrials.gov/search?cond=${article.id}`} target="_blank">pour consulter l'article</a></strong>
                <p>{article.abstract}</p>
              </li>
            ))}
          </ul>

          <h3>PubMed</h3>
          <ul>
            {results.pubmed.length === 0 && <li>Aucun résultat</li>}
            {results.pubmed.map((article) => (
              <li key={article.id}>
                <strong>{article.title} - <a className="lien" href={`https://pubmed.ncbi.nlm.nih.gov/${article.id}/`} target="_blank">pour consulter l'article</a></strong>
                <p>{article.abstract}</p>
              </li>
            ))}
          </ul>
        </>
      )}


      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}