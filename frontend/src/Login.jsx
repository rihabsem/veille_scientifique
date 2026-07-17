import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import "./css/login.css";

export default function Login() {
    const navigate = useNavigate();

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
        <form className='formulaire' onSubmit={handleSubmit}>
            <label className="form-label">Email :</label>
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

            <label className="form-label">Password :</label>
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

            <button className="btn btn-primary" type="submit">
                Login
            </button><br/>

            {errors.general && (
                <p className="error-message">{errors.general}</p>
            )}

            <br />

            <a className="reg" href="/register">S'inscrire</a>
        </form>
    );
}