import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";
import Header from "./components/Header";
import HelpTooltip from "./components/HelpTooltip";
import Spinner from "./components/Spinner";
import { useLanguage } from "./i18n/LanguageContext";
import "./css/login.css";
import "./css/userdata.css";

export default function UserData() {
    const navigate = useNavigate();
    const { t } = useLanguage();

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [form, setForm] = useState({
        profile: "",
        update_rate: ""
    });

    // Sauvegarde le profil initial
    const [initialProfile, setInitialProfile] = useState("");

    const hasFetched = useRef(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!form.profile.trim()) {
            setError("Le profil est obligatoire.");
            return;
        }

        if (!form.update_rate) {
            setError("Veuillez choisir une fréquence.");
            return;
        }

        setError("");

        try {
            await API.post("/update", form);
            if (form.profile.trim() !== initialProfile.trim()) {
                navigate("/questions/start");
                return;
            }

            alert("Profil mis à jour avec succès.");

        } catch (err) {
            console.log(err.response?.status);
            console.log(err.response?.data);

            setError(
                err.response?.data?.detail ||
                "Erreur lors de la mise à jour."
            );
        }
    };

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        const fetchUserData = async () => {
            try {
                const response = await API.get("/data");

                setData(response.data);

                setForm({
                    profile: response.data.profil,
                    update_rate: response.data.weekly_monthly
                });
                setInitialProfile(response.data.profil);

            } catch (err) {
                setError(
                    err.response?.data?.detail ||
                    "Erreur lors du chargement."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, []);

    return (
        <>
            <Header userName={data?.nom ?? null} />
            <div className="page">
                {loading ? (
                    <Spinner />
                ) : error && !data ? (
                    <p className="error-message">{error}</p>
                ) : (
                    <div className="card userdata-card">
                        <h2>{t("userdata.title")}</h2>

                        <form onSubmit={handleSubmit}>

                            <label className="form-label">{t("userdata.nameLabel")}</label><br />

                            <input
                                disabled
                                type="text"
                                className="form"
                                value={data.nom}
                                readOnly
                            />

                            <label className="form-label">{t("userdata.emailLabel")}</label><br />

                            <input
                                disabled
                                type="text"
                                className="form"
                                value={data.email}
                                readOnly
                            />

                            <div className="field-label-row">
                                <label className="form-label">{t("userdata.profileLabel")}</label>
                                <HelpTooltip text={`${t("register.profileHelp")} ${t("register.profileExample")}`} />
                            </div>

                            <textarea
                                className="form-area"
                                value={form.profile}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        profile: e.target.value
                                    })
                                }
                            />

                            <div className="field-label-row">
                                <label className="form-label">{t("userdata.rateLabel")}</label>
                                <HelpTooltip text={t("register.rateHelp")} />
                            </div>

                            <select
                                className="form"
                                value={form.update_rate}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        update_rate: e.target.value
                                    })
                                }
                            >
                                <option value="weekly">{t("register.rateWeekly")}</option>
                                <option value="monthly">{t("register.rateMonthly")}</option>
                            </select>

                            <button className="btn btn-primary formulaire__submit" type="submit">
                                {t("userdata.submitButton")}
                            </button>

                        </form>

                        {error && (
                            <p className="error-message">{error}</p>
                        )}
                    </div>
                )}
            </div>
        </>
    );
}
