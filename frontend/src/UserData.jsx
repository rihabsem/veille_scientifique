import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "./api";

export default function UserData() {
    const navigate = useNavigate();

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
                navigate("/questions");
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

    if (loading) return <p>Chargement...</p>;

    if (error && !data)
        return <p>{error}</p>;

    return (
        <div>
            <h2>Profil utilisateur</h2>

            <form onSubmit={handleSubmit}>

                <label>Nom</label><br />

                <input
                    disabled
                    type="text"
                    value={data.nom}
                    readOnly
                />

                <br /><br />

                <label>Email</label><br />

                <input
                    disabled
                    type="text"
                    value={data.email}
                    readOnly
                />

                <br /><br />

                <label>Profil</label><br />

                <textarea
                    value={form.profile}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            profile: e.target.value
                        })
                    }
                />

                <br /><br />

                <label>Cadence de mise à jour</label><br />

                <select
                    value={form.update_rate}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            update_rate: e.target.value
                        })
                    }
                >
                    <option value="weekly">Hebdomadaire</option>
                    <option value="monthly">Mensuelle</option>
                </select>

                <br /><br />

                <button type="submit">
                    Mettre à jour
                </button>

            </form>

            {error && (
                <p style={{ color: "red" }}>
                    {error}
                </p>
            )}
        </div>
    );
}