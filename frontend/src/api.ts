import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://warehouse-api-y1mn.onrender.com",
  timeout: 30000,
});

export default api;