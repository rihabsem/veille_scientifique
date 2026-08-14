import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import Header from "./components/Header";
import Spinner from "./components/Spinner";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/qsts.css";

const Questions = () => {
  const { t } = useLanguage();

  const [currentQuestion, setCurrentQuestion] = useState(null); // texte de la question affichée
  const [currentAnswer, setCurrentAnswer] = useState("");       // réponse en cours de saisie
  const [history, setHistory] = useState([]);                    // [{question, answer}, ...] déjà validées
  const [isLast, setIsLast] = useState(false);

  const [loading, setLoading] = useState(true);       // chargement initial
  const [submitting, setSubmitting] = useState(false); // appel réseau en cours (next / set-results)
  const [error, setError] = useState(null);            // erreur bloquante (chargement initial)
  const [fieldError, setFieldError] = useState("");     // erreur de validation du champ courant
  const [generalError, setGeneralError] = useState(""); // erreur lors de la soumission

  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const authHeaders = {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
  };

  // --- Chargement de la première question ---
  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const fetchFirstQuestion = async () => {
      try {
        const response = await API.get("/questions/start", authHeaders);
        setCurrentQuestion(response.data.question);
        setIsLast(response.data.is_last);
      } catch (err) {
        setError(err.response?.data?.detail || "Erreur lors du chargement");
      } finally {
        setLoading(false);
      }
    };
    fetchFirstQuestion();
  }, []);

  const handleNext = async (e) => {
    e.preventDefault();
    setFieldError("");
    setGeneralError("");

    if (!currentAnswer.trim()) {
      setFieldError("Veuillez remplir ce champ.");
      return;
    }

    const updatedHistory = [
      ...history,
      { question: currentQuestion, answer: currentAnswer }
    ];

    setSubmitting(true);
    try {
      if (isLast) {
        // Dernière question répondue -> on envoie tout
        await API.post("/set-results", { answers: updatedHistory }, authHeaders);
        navigate("/dashboard");
        return;
      }

      // Sinon, on demande la question suivante
      const response = await API.post(
        "/questions/next",
        { previous: updatedHistory },
        authHeaders
      );

      setHistory(updatedHistory);
      setCurrentQuestion(response.data.question);
      setIsLast(response.data.is_last);
      setCurrentAnswer("");
    } catch (err) {
      if (err.response?.status === 422) {
        setGeneralError(err.response.data.detail[0].msg);
      } else {
        setGeneralError(
          err.response?.data?.detail || "Une erreur est survenue."
        );
      }
    } finally {
      setSubmitting(false);
    }
  };

  const stepNumber = history.length + 1;

  return (
    <>
      <Header />
      <div className="page">
        {loading ? (
          <Spinner />
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : (
          <div className="card questions-card">
            <h2>{t("questions.title")}</h2>
            <p className="questions-intro">{t("questions.intro")}</p>

            <p className="questions-progress">
              {stepNumber} / 3
            </p>

            <form onSubmit={handleNext}>
              <div>
                <label className="form-label">{currentQuestion}</label>
                <br />
                <textarea
                  className={`textarea-form ${fieldError ? "input-error" : ""}`}
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  disabled={submitting}
                />
                <br />
                {fieldError && <p className="error-message">{fieldError}</p>}
              </div>

              <button className="btn btn-primary" type="submit" disabled={submitting}>
                {submitting
                  ? t("questions.loading") || "..."
                  : isLast
                  ? t("questions.submitButton")
                  : t("questions.nextButton") || "Suivant"}
              </button>

              {generalError && <p className="error-message">{generalError}</p>}
            </form>
          </div>
        )}
      </div>
    </>
  );
};

export default Questions;