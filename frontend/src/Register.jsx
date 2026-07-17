import React, { useState } from "react";
import {useNavigate} from "react-router-dom";
import API from "./api";
import "./css/login.css";

const Register = () => {
  const [form, setForm] = useState({
    name:"",
    email:"",
    password:"",
    profile:"",
    update_rate:""
  });

  const [errors, setErrors] = useState({
    name:"",
    email:"",
    password:"",
    profile:"",
    rate:"",
    general:""
  })


  const navigate = useNavigate();
  const isValidEmail = (email) => {
        const emailRegex = /^[a-zA-Z]+\.[a-zA-Z]+@ulb.be$/
        return emailRegex.test(email);
    }
  const isValidPassword = (password) => {
    const passwordRegex = /^[a-zA-Z0-9@_-]{8,}$/
    return passwordRegex.test(password);
  }

  
    
  const handleSubmit = async(e) => {
    setErrors({
      name:"",
      email:"",
      password:"",
      profile:"",
      update_rate:""
    })

    let newErrors = {};

    e.preventDefault();
    if (!form.name.trim()) {
      newErrors.name = "Veuillez remplir tous les champs.";
    }

    if ( !form.email.trim()) {
      newErrors.email = "Veuillez remplir tous les champs.";
    }
    if (!form.password.trim()) {
      newErrors.name = "Veuillez remplir tous les champs.";
    }

    if (!form.profile.trim()) {
      newErrors.profile = "Veuillez remplir tous les champs.";
    }

    if (!form.update_rate.trim()) {
      newErrors.update_rate = "Veuillez remplir tous les champs.";
    }
    // if (!isValidEmail(form.email)) {
    //     newErrors.email="Veuillez utiliser un email valide de l'ULB (ex:prenom.nom@ulb.be)";
    // }
    if(!isValidPassword(form.password)){
      newErrors.password="Le mot de passe doit être d'une longeur minimal de 8 caractères"
    }
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    try{
      await API.post("/register", form);

      // Login automatique juste après l'inscription pour récupérer un token
      const loginResponse = await API.post("/login", {
        email: form.email,
        password: form.password
      });
      localStorage.setItem("token", loginResponse.data.access_token);
      alert("token : " + loginResponse.data.access_token);
      navigate("/questions");
    }
    catch(err){
      if(err.response?.status == 422){
              setErrors({
        ...errors,
        general: ""
        });
            }
            else{               
              setErrors({
                name:"",
                email:"",
                password:"",
                profile:"",
                update_rate:"",
                general:
                err.response?.data?.detail ||
                "Une erreur est survenue."
              })
    }
    }
}
  return(
    <form className='formulaire' onSubmit={handleSubmit}>
      <label className='form-label'>Nom:</label><br/>
      <input className={`form ${errors.name? "input-error":""}`} type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}/><br/>
      {errors.name && (
                <p className="error-message">{errors.name}</p>
            )}
      <label className='form-label'>Email:</label><br/>
      <input className={`form ${errors.email? "input-error":""}`} type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}/><br/>
      {errors.email && (
                <p className="error-message">{errors.email}</p>
            )}
      <label className='form-label'>Mot de passe:</label><br/>
      <input className={`form ${errors.password? "input-error":""}`} type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
      {errors.password && (
                <p className="error-message">{errors.password}</p>
            )}
      <label className='form-label'>Profil:</label><br/>
      <textarea className={`form-area ${errors.profile? "input-error":""}`} value={form.profile} onChange={(e) => setForm({...form, profile: e.target.value})}/><br/>
      {errors.profile && (
                <p className="error-message">{errors.profile}</p>
            )}
      <label className='form-label'>Cadence de mise a jour:</label><br/>
      <select
      className={`form ${errors.update_rate? "input-error":""}`}
        value={form.update_rate}
        onChange={(e) =>
          setForm({ ...form, update_rate: e.target.value })
        }
      >
        <option value="">-- Sélectionner --</option>
        <option value="weekly">Hebdomadairement</option>
        <option value="monthly">Mensuellement</option>
      </select><br/>
      {errors.update_rate && (
                <p className="error-message">{errors.update_rate}</p>
            )}
      <button className="btn" type="submit">S'inscrire</button> 
      {errors.general && (
                <p className="error-message">{errors.general}</p>
            )}  
    </form>
  );
};

export default Register;