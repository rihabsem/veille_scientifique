import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import Header from "./components/Header";
import Spinner from "./components/Spinner";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/qsts.css";

const Questions = () => {
  const { t } = useLanguage();

  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [history, setHistory] = useState([]);
  const [isLast, setIsLast] = useState(false);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [fieldError, setFieldError] = useState("");
  const [generalError, setGeneralError] = useState("");

  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const authHeaders = {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
  };

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
        await API.post("/set-results", { answers: updatedHistory }, authHeaders);
        navigate("/dashboard");
        return;
      }
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