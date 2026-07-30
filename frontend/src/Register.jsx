import React, { useState } from "react";
import {useNavigate} from "react-router-dom";
import API from "./api";
import Header from "./components/Header";
import HelpTooltip from "./components/HelpTooltip";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/login.css";

const Register = () => {
  const { t } = useLanguage();
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
        const emailRegex = /^[A-Za-z]+\.[A-Za-z]+@[A-Za-z0-9-]+\.[A-Za-z]+$/
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
    if (!isValidEmail(form.email)) {
        newErrors.email="Veuillez utiliser un email valide";
    }
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
    <>
      <Header />
      <div className="page">
        <h2 style={{ textAlign: "center" }}>{t("register.title")}</h2>
        <form className='formulaire card' onSubmit={handleSubmit}>
          <label className='form-label'>{t("register.nameLabel")}</label><br/>
          <input className={`form ${errors.name? "input-error":""}`} type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}/><br/>
          {errors.name && (
                    <p className="error-message">{errors.name}</p>
                )}
          <label className='form-label'>{t("register.emailLabel")}</label><br/>
          <input className={`form ${errors.email? "input-error":""}`} type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} placeholder="prenom.nom@ulb.be"/><br/>
          {errors.email && (
                    <p className="error-message">{errors.email}</p>
                )}
          <label className='form-label'>{t("register.passwordLabel")}</label><br/>
          <input placeholder={t("register.passwordCaracters")} className={`form ${errors.password? "input-error":""}`} type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
          {errors.password && (
                    <p className="error-message">{errors.password}</p>
                )}
          <div className="field-label-row">
            <label className='form-label'>{t("register.profileLabel")}</label>
            <HelpTooltip text={`${t("register.profileHelp")} ${t("register.profileExample")}`} />
          </div>
          <textarea className={`form-area ${errors.profile? "input-error":""}`} value={form.profile} onChange={(e) => setForm({...form, profile: e.target.value})}/><br/>
          {errors.profile && (
                    <p className="error-message">{errors.profile}</p>
                )}
          <div className="field-label-row">
            <label className='form-label'>{t("register.rateLabel")}</label>
            <HelpTooltip text={t("register.rateHelp")} />
          </div>
          <select
          className={`form ${errors.update_rate? "input-error":""}`}
            value={form.update_rate}
            onChange={(e) =>
              setForm({ ...form, update_rate: e.target.value })
            }
          >
            <option value="">{t("register.rateSelect")}</option>
            <option value="weekly">{t("register.rateWeekly")}</option>
            <option value="monthly">{t("register.rateMonthly")}</option>
          </select><br/>
          {errors.update_rate && (
                    <p className="error-message">{errors.update_rate}</p>
                )}
          <button className="btn btn-primary formulaire__submit" type="submit">{t("register.submitButton")}</button>
          {errors.general && (
                    <p className="error-message">{errors.general}</p>
                )}
        </form>
      </div>
    </>
  );
};

export default Register;
