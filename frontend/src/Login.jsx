import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import Header from "./components/Header";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/login.css";

export default function Login() {
    const navigate = useNavigate();
    const { t } = useLanguage();

    const [form, setForm] = useState({
        email: "",
        password: ""
    });

    const [errors, setErrors] = useState({
        email: "",
        password: "",
        general: ""
    });

    const isValidEmail = (email) => {
        const emailRegex = /^[a-zA-Z]+\.[a-zA-Z]+@ulb\.be$/;
        return emailRegex.test(email);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Réinitialise les erreurs
        setErrors({
            email: "",
            password: "",
            general: ""
        });

        let newErrors = {};

        // if (!form.email.trim()) {
        //     newErrors.email = "Veuillez saisir votre email.";
        // } else if (!isValidEmail(form.email)) {
        //     newErrors.email =
        //         "Veuillez utiliser un email valide de l'ULB (ex : prenom.nom@ulb.be).";
        // }

        if (!form.password.trim()) {
            newErrors.password = "Veuillez saisir votre mot de passe.";
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            const response = await API.post("/login", form);

            localStorage.setItem("token", response.data.access_token);
            navigate("/dashboard");
        } catch (err) {
            if(err.response?.status == 422){
                setErrors({
                email: "",
                password: "",
                general: err.response.data.detail[0].msg
            });
            }
            else if (err.response?.status === 401) {
            setErrors({
                email: "",
                password: err.response?.data?.detail || "Email ou mot de passe incorrect.",
                general: ""
            });
            }
            else{
                setErrors({
                email: "",
                password: "",
                general:
                    err.response?.data?.detail ||
                    "Une erreur est survenue."
            });
            }

        }
    };

    return (
        <>
            <Header />
            <div className="page landing">
                <section className="hero">
                    <h1>{t("login.heroTitle")}</h1>
                    <p className="hero__subtitle">{t("login.heroSubtitle")}</p>
                </section>

                <section className="how-it-works">
                    <h2>{t("login.howItWorksTitle")}</h2>
                    <div className="how-it-works__steps">
                        <div className="how-it-works__step">
                            <h3>{t("login.step1Title")}</h3>
                            <p>{t("login.step1Desc")}</p>
                        </div>
                        <div className="how-it-works__step">
                            <h3>{t("login.step2Title")}</h3>
                            <p>{t("login.step2Desc")}</p>
                        </div>
                        <div className="how-it-works__step">
                            <h3>{t("login.step3Title")}</h3>
                            <p>{t("login.step3Desc")}</p>
                        </div>
                    </div>
                </section>

                <form className='formulaire card' onSubmit={handleSubmit}>
                    <label className="form-label">{t("login.emailLabel")}</label>
                    <br />

                    <input
                        type="email"
                        className={`form ${errors.email ? "input-error" : ""}`}
                        placeholder="prenom.nom@ulb.be"
                        value={form.email}
                        onChange={(e) =>
                            setForm({ ...form, email: e.target.value })
                        }
                    />

                    {errors.email && (
                        <p className="error-message">{errors.email}</p>
                    )}

                    <label className="form-label">{t("login.passwordLabel")}</label>
                    <br />

                    <input
                        type="password"
                        className={`form ${errors.password ? "input-error" : ""}`}
                        value={form.password}
                        onChange={(e) =>
                            setForm({ ...form, password: e.target.value })
                        }
                    />

                    {errors.password && (
                        <p className="error-message">{errors.password}</p>
                    )}

                    <button className="btn btn-primary formulaire__submit" type="submit">
                        {t("login.loginButton")}
                    </button>
                    <a className="reset-password" href="/mot-de-passe-oublier">
                            {t("login.mpdOublier")}
                        </a>

                    {errors.general && (
                        <p className="error-message">{errors.general}</p>
                    )}

                    <div className="formulaire__register-cta">
                        <span>{t("login.noAccount")}</span>
                        <a className="btn btn-secondary" href="/register">
                            {t("login.registerCta")}
                        </a>
                    </div>
                </form>
            </div>
        </>
    );
}
