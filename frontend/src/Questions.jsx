import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";

const Questions = () => {
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const hasFetched = useRef(false);
  const [answers, setAnswers] = useState({
    question1:"",
    question2:"",
    question3:""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if(!answers.question1.trim() || !answers.question2.trim() || !answers.question3.trim()) {
      alert("Veuillez remplir toutes les questions.");
      return;
    }
    try{
      const response = await API.post("/set-results", answers, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      navigate("/dashboard");

    }
    catch(err){
      console.log(err.response?.data);
      alert(err.response?.data?.detail || err.message);
    }

  }

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const fetchQuestions = async () => {
      const token = localStorage.getItem("token");
      try {
        const response = await API.get("/questions", {
          headers: { Authorization: `Bearer ${token}` }
        });
        setQuestions(response.data);
        
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
      <form onSubmit={handleSubmit}>
      {questions.map((question, index) => (
        <div key={index}>
          <label>{question}</label><br/>
          <textarea value={answers[`question${index + 1}`]} onChange={(e) => setAnswers({...answers, [`question${index + 1}`]: e.target.value})} /><br/>
        </div>
      ))}
      
      <button>Soumettre</button>
      </form>
    </div>
    
  );
};

export default Questions;