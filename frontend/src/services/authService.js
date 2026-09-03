import api from "./api";

function persistSession(data, email = "") {
  localStorage.setItem("access_token", data.access_token);
  if (email) localStorage.setItem("user_email", email);
}

export async function signup(email, password) {
  const normalizedEmail = email.trim().toLowerCase();
  const response = await api.post("/auth/signup", { email: normalizedEmail, password });
  persistSession(response.data, normalizedEmail);
  return response.data;
}

export async function login(email, password) {
  const normalizedEmail = email.trim().toLowerCase();
  const response = await api.post("/auth/login", { email: normalizedEmail, password });
  persistSession(response.data, normalizedEmail);
  return response.data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_email");
}

export function isLoggedIn() {
  return Boolean(localStorage.getItem("access_token"));
}

export function isAdmin() {
  const token = localStorage.getItem("access_token");
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return Boolean(payload.is_admin);
  } catch {
    return false;
  }
}

export async function googleLogin(credential) {
  const response = await api.post("/auth/google", { credential });
  persistSession(response.data);
  return response.data;
}
