import React, { useState } from "react";
import API from "./api";

const Register = () => {
  const [form, setForm] = useState({
    name:"",
    email:"",
    password:"",
    update_rate:""
  })
  return(
    <form>
      <label>Nom:</label><br/>
      <input type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}/><br/>
      <label>Email:</label><br/>
      <input type="text" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}/><br/>
      <label>Mot de passe:</label><br/>
      <input type="text" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}/><br/>
      <label>Cadence de mise a jour:</label><br/>
      <select
        value={form.update_rate}
        onChange={(e) =>
          setForm({ ...form, update_rate: e.target.value })
        }
      >
        <option value="">-- Sélectionner --</option>
        <option value="weekly">Hebdomadairement</option>
        <option value="monthly">Mensuellement</option>
      </select>    
    </form>
  );
};

export default Register;