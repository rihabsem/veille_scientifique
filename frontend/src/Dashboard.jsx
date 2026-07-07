import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    // localStorage.removeItem("questions");
    navigate("/");
  };

  return (
    <div>
      <h1>Bienvenue !</h1>
      
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}