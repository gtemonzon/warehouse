import axios from "axios";

const api = axios.create({
  baseURL: "/api",   // ← Vite lo redirige internamente al 8000
  timeout: 15000,
});

export default api;
