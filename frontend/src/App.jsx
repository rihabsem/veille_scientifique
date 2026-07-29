import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import Register from './Register';
import Questions from './Questions'; 
import PrivateRoute from './PrivateRoute'; 
import UserData from './UserData';
import ForgotPassword from "./ForgotPassword";
import ResetPassword from "./ResetPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        } />
        <Route path="/register" element={<Register />} />
        <Route path="/questions" 
        element={
          <PrivateRoute>
            <Questions />
          </PrivateRoute>
        } />
        <Route path="/user-data" element={
          <PrivateRoute>
            <UserData/>
          </PrivateRoute>
        }/>
      </Routes>

      <Route path="/mot-de-passe-oublier" 
        element={
          <PrivateRoute>
            <ForgotPassword />
          </PrivateRoute>
        } />
        <Route path="/mot-de-passe-reinitier" 
        element={
          <PrivateRoute>
            <ResetPassword />
          </PrivateRoute>
        } />
    </BrowserRouter>
  );
}

export default App;