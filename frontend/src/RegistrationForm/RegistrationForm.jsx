import React, {useState} from 'react';
import axios from 'axios';
import './RegistrationForm.css';
import { withRouter } from "react-router-dom";

function RegistrationForm(){
    const [form, setForm] = useState({
        email:"",
        password:"",
        userName:"",
        profile_description:"",
        update_rate:""
    })
    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Registration attempted");
        
        };
    return (

        <form onSubmit={handleSubmit}>

            <input
                type="text"
                name="nom"
                placeholder="Name"
                value={form.nom}
                onChange={handleChange}
            />

            <input
                type="email"
                name="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
            />

            <input
                type="password"
                name="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
            />

            <input
                type="text"
                name="profil"
                placeholder="Profile"
                value={form.profil}
                onChange={handleChange}
            />

            <select
                name="weekly_monthly"
                value={form.weekly_monthly}
                onChange={handleChange}
            >
                <option value="">Choose...</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
            </select>

            <button type="submit">
                Register
            </button>

        </form>

    );

}
export default RegistrationForm;