import axios from "axios";

const API = axios.create({
    baseURL: "https://gallstone-botanical-reps.ngrok-free.dev", //this should be localhost 8000
    withCredentials: true,//added this
  headers: {//added this
    'ngrok-skip-browser-warning': 'true',//added this
  }, //added this
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