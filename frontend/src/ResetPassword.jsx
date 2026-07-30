import React, { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import API from "./api";
import "./css/login.css";
import Header from "./components/Header";
import HelpTooltip from "./components/HelpTooltip";
import Spinner from "./components/Spinner";
import { useLanguage } from "./i18n/LanguageContext";

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const navigate = useNavigate();

    const [form, setForm] = useState({ password: "", confirmPassword: "" });
    const [errors, setErrors] = useState({ password: "", confirmPassword: "", general: "" });
    const [success, setSuccess] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({ password: "", confirmPassword: "", general: "" });

        if (!token) {
            setErrors({
                password: "",
                confirmPassword: "",
                general: "Lien invalide : jeton manquant."
            });
            return;
        }

        let newErrors = {};
        if (!form.password.trim()) {
            newErrors.password = "Veuillez saisir un nouveau mot de passe.";
        } else if (form.password.length < 8) {
            newErrors.password = "Le mot de passe doit contenir au moins 8 caractères.";
        }

        if (form.password !== form.confirmPassword) {
            newErrors.confirmPassword = "Les mots de passe ne correspondent pas.";
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors({ ...newErrors, general: "" });
            return;
        }

        setIsSubmitting(true);
        try {
            await API.post("/reset-password", {
                token,
                new_password: form.password
            });
            setSuccess(true);
            setTimeout(() => navigate("/"), 3000);
        } catch (err) {
            setErrors({
                password: "",
                confirmPassword: "",
                general: err.response?.data?.detail || "Une erreur est survenue."
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!token) {
        return (
            <>
            <div className="formulaire">
                <p className="error-message">
                    Lien de réinitialisation invalide ou incomplet.
                </p>
                <Link to="/forgot-password">Demander un nouveau lien</Link>
            </div>
            </>
        );
    }

    if (success) {
        return (
            <>
            <div className="formulaire">
                <p>
                    Votre mot de passe a été réinitialisé avec succès.
                    Vous allez être redirigé vers la page de connexion...
                </p>
            </div>
            </>
        );
    }

    return (
        <>
        <Header />
        <form className="formulaire" onSubmit={handleSubmit}>
            <h2>Réinitialiser le mot de passe</h2>

            <label className="form-label">Nouveau mot de passe :</label>
            <br />
            <input
                type="password"
                className={`form ${errors.password ? "input-error" : ""}`}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            {errors.password && <p className="error-message">{errors.password}</p>}

            <label className="form-label">Confirmer le mot de passe :</label>
            <br />
            <input
                type="password"
                className={`form ${errors.confirmPassword ? "input-error" : ""}`}
                value={form.confirmPassword}
                onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
            />
            {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}

            <br />
            <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Réinitialisation..." : "Réinitialiser le mot de passe"}
            </button>
            <br />

            {errors.general && <p className="error-message">{errors.general}</p>}
        </form>
        </>
    );
}