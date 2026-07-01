import Login from "./Login";
import Dashboard from "./Dashboard";

function App() {
  const path = window.location.pathname;
  return path === "/dashboard" ? <Dashboard /> : <Login />;
}

export default App;