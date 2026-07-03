import React, { useState } from "react";
import {useNavigate} from "react-router-dom";
import API from "./api";

const Register = () => {
  const [form, setForm] = useState({
    name:"",
    email:"",
    password:"",
    profile:"",
    update_rate:""
  });
  const navigate = useNavigate();
  const handleSubmit = async(e) => {
    e.preventDefault();
    try{
      const response = await API.post("/register", form);

      navigate("/");
    }
    catch(err){
      console.log(err.response?.data);  // <-- le détail exact ici
      alert(err.response?.data?.detail || err.message);
    }
  }
  return(
    <form onSubmit={handleSubmit}>
      <label>Nom:</label><br/>
      <input type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}/><br/>
      <label>Email:</label><br/>
      <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}/><br/>
      <label>Mot de passe:</label><br/>
      <input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
      <label>Profil:</label><br/>
      <textarea value={form.profile} onChange={(e) => setForm({...form, profile: e.target.value})}/><br/>
      <label>Cadence de mise a jour:</label><br/>
      <select
        value={form.update_rate}
        onChange={(e) =>
          setForm({ ...form, update_rate: e.target.value })
        }
      >
        <option value="">-- Sélectionner --</option>
        <option value="weekly">Hebdomadairement</option>
        <option value="monthly">Mensuellement</option>
      </select><br/>
      <button type="submit">S'inscrire</button>   
    </form>
  );
};

export default Register;