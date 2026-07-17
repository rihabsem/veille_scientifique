import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import "./css/qsts.css";

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
  const [errors, setErrors] = useState({
          qst1: "",
          qst2: "",
          qst3: "",
          general:""
      });
  const handleSubmit = async (e) => {
    setErrors({
      qst1:"",
      qst2:"",
      qst3:"",
      general:""
    })
    let newErrors = {}
    e.preventDefault();
    if(!answers.question1.trim()){
      newErrors.qst1="Veuillez remplir tous les champs.";
    }

    if(!answers.question2.trim()){
      newErrors.qst2="Veuillez remplir tous les champs.";
    }

    if(!answers.question3.trim()){
      newErrors.qst3="Veuillez remplir tous les champs.";
    }
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    
    try{
      const response = await API.post("/set-results", answers, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      navigate("/dashboard");

    }
    catch(err){
      if(err.response?.status == 422){
          setErrors({
        ...errors,
        general: err.response.data.detail[0].msg
        });
      }
      else{               
        setErrors({
          qst1:"",
          qst2:"",
          qst3:"",
          general:
          err.response?.data?.detail ||
          "Une erreur est survenue."
              })
    }
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
        <label className="form-label">{question}</label><br/>
        <textarea
          className={`textarea-form ${errors[`qst${index + 1}`] ? "input-error" : ""}`}
          value={answers[`question${index + 1}`]}
          onChange={(e) => setAnswers({...answers, [`question${index + 1}`]: e.target.value})}
        /><br/>
        {errors[`qst${index + 1}`] && (
          <p className="error-message">{errors[`qst${index + 1}`]}</p>
        )}
      </div>
    ))}

    <button className="btn-inscrire">Soumettre</button>

    {errors.general && (
      <p className="error-message">{errors.general}</p>
    )}
    </form>
  </div>
);
};

export default Questions;