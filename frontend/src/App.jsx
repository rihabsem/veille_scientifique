import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import Register from './Register';
import Questions from './Questions'; 
import PrivateRoute from './PrivateRoute'; 
import UserData from './UserData';

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
        <Route path="/user-data" element={<UserData/>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;