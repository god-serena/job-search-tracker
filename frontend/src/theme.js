import { ref } from "vue";

const COOKIE_NAME = "theme";
const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;
const preference = ref("dark");

function readPreference() {
  try {
    const entry = document.cookie
      .split(";")
      .map((cookie) => cookie.trim())
      .find((cookie) => cookie.startsWith(`${COOKIE_NAME}=`));
    const value = entry ? decodeURIComponent(entry.slice(COOKIE_NAME.length + 1)) : "";
    return value === "light" || value === "dark" ? value : "dark";
  } catch {
    return "dark";
  }
}

function applyPreference(value) {
  preference.value = value === "light" || value === "dark" ? value : "dark";
  try {
    document.documentElement.dataset.theme = preference.value;
  } catch {
    // Keep the in-memory preference usable when the document is unavailable.
  }
}

export function setTheme(value) {
  applyPreference(value);
  try {
    document.cookie = `${COOKIE_NAME}=${encodeURIComponent(preference.value)}; Max-Age=${ONE_YEAR_SECONDS}; Path=/; SameSite=Lax`;
  } catch {
    // Theme application remains effective even if persistence is unavailable.
  }
}

export function useTheme() {
  return preference;
}

applyPreference(readPreference());
