import api from "./api";

export async function signup(email, password) {
  const response = await api.post("/auth/signup", { email, password });
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

export async function login(email, password) {
  const response = await api.post("/auth/login", { email, password });
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

export async function googleAuth(credential) {
  const response = await api.post("/auth/google", { credential });
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("is_admin");
}

export function isLoggedIn() {
  return !!localStorage.getItem("access_token");
}

export function isAdmin() {
  const token = localStorage.getItem("access_token");
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return !!payload.is_admin;
  } catch {
    return false;
  }
}
