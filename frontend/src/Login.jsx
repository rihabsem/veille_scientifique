import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";

export default function Login() {
    const [form, setForm] = useState({
        email: "",
        password: ""
    });
    const navigate = useNavigate();
    const isValidEmail = (email) => {
        const emailRegex = /^[a-zA-Z]+\.[a-zA-Z]+@ulb.be$/
        return emailRegex.test(email);
    }
    const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email.trim() || !form.password.trim()) {
            alert("Veuillez remplir tous les champs.");
            return;
        }
    if (!isValidEmail(form.email)) {
        alert("Veuillez utiliser un email valide de l'ULB (ex:prenom.nom@ulb.be)");
        return;
    }


    try {

        const response = await API.post("/login", form);

        localStorage.setItem(
            "token",
            response.data.access_token
        );
        navigate("/dashboard");
    } catch (err) {

        alert(err.response?.data?.detail || err.message);

    }
};
  return (
    <form onSubmit={handleSubmit}>
       <label>Email:</label><br/>
      <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}/><br/>
      <label>Password:</label><br/> 
      <input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
      <button type="submit">Login</button><br/>
      <a href="/register">S'inscrire</a>
    </form>
  );

  
}