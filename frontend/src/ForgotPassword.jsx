import React, { useState } from "react";
import { Link } from "react-router-dom";
import API from "./api";
import "./css/login.css";

export default function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [errors, setErrors] = useState({ email: "", general: "" });
    const [submitted, setSubmitted] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const isValidEmail = (value) => {
        const emailRegex = /^[a-zA-Z]+\.[a-zA-Z]+@ulb\.be$/;
        return emailRegex.test(value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({ email: "", general: "" });

        if (!email.trim()) {
            setErrors({ email: "Veuillez saisir votre email.", general: "" });
            return;
        }
        // if (!isValidEmail(email)) {
        //     setErrors({
        //         email: "Veuillez utiliser un email valide de l'ULB (ex : prenom.nom@ulb.be).",
        //         general: ""
        //     });
        //     return;
        // }

        setIsSubmitting(true);
        try {
            await API.post("/forgot-password", { email });
            setSubmitted(true);
        } catch (err) {
            setErrors({
                email: "",
                general: err.response?.data?.detail || "Une erreur est survenue."
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <div className="formulaire">
                <p>
                    Si un compte existe avec cet email, un lien de réinitialisation
                    vient de vous être envoyé. Vérifiez votre boîte de réception (et vos spams).
                </p>
                <Link to="/">Retour à la connexion</Link>
            </div>
        );
    }

    return (
        <form className="formulaire" onSubmit={handleSubmit}>
            <h2>Mot de passe oublié</h2>
            <p>Saisissez votre email pour recevoir un lien de réinitialisation.</p>

            <label className="form-label">Email :</label>
            <br />
            <input
                type="email"
                className={`form ${errors.email ? "input-error" : ""}`}
                placeholder="prenom.nom@ulb.be"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            {errors.email && <p className="error-message">{errors.email}</p>}

            <br />
            <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Envoi..." : "Envoyer le lien"}
            </button>
            <br />

            {errors.general && <p className="error-message">{errors.general}</p>}

            <br />
            <Link to="/">Retour à la connexion</Link>
        </form>
    );
}