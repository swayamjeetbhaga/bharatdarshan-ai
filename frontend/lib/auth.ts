import api from "./api";

export const signup = async (email: string, username: string, password: string) => {
  const res = await api.post("/api/v1/auth/signup", { email, username, password });
  return res.data;
};

export const login = async (email: string, password: string) => {
  const res = await api.post("/api/v1/auth/login", { email, password });
  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem("refresh_token", res.data.refresh_token);
  return res.data;
};

export const logout = async () => {
  const refresh_token = localStorage.getItem("refresh_token");
  await api.post("/api/v1/auth/logout", { refresh_token });
  localStorage.clear();
  window.location.href = "/login";
};

export const isLoggedIn = () => {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
};