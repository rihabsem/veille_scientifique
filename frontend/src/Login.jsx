import React, { useState } from "react";
import API from "./api";

export default function Login() {
    const [form, setForm] = useState({
        email: "",
        password: ""
    });
    const handleSubmit = async (e) => {
    e.preventDefault();

    try {

        const response = await API.post("/login", form);

        localStorage.setItem(
            "token",
            response.data.access_token
        );
        window.location.href = "/dashboard";
    } catch (err) {

        alert(err);

    }
};
  return (
    <form onSubmit={handleSubmit}>
       <label>Email:</label><br/>
      <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}/><br/>
      <label>Password:</label><br/> 
      <input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
      <button type="submit">Login</button>
    </form>
  );

  
}