import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";

const Questions = () => {
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const cached = localStorage.getItem("questions");
    if (cached) {
      setQuestions(JSON.parse(cached));
      setLoading(false);
      return; // on ne fait pas l'appel API
    }

    const fetchQuestions = async () => {
      const token = localStorage.getItem("token");
      try {
        const response = await API.get("/questions", {
          headers: { Authorization: `Bearer ${token}` }
        });
        setQuestions(response.data);
        localStorage.setItem("questions", JSON.stringify(response.data));
      } catch (err) {
        setError(err.response?.data?.detail || "Erreur lors du chargement");
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  if (loading) return <p>Chargement...</p>;
  if (error) return <p>Erreur: {error}</p>;

  return (
    <div>
      <h2>Questions</h2>
      {questions.map((question, index) => (
        <div key={index}>
          <label>{question}</label><br/>
          <textarea /><br/>
        </div>
      ))}
    </div>
  );
};

export default Questions;