import axios from "axios";

const API = axios.create({
  baseURL: "https://gallstone-botanical-reps.ngrok-free.dev",
  // baseURL: "https://research.lphys-ulb.net", 
    withCredentials: true,
  headers: {
    'ngrok-skip-browser-warning': 'true',
  },
});

API.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");

      window.location.href = "/";
    }

    return Promise.reject(error);
  }
);
export default API;