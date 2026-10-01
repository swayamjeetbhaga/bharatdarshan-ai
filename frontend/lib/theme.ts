export type Theme = "light" | "dark";

const STORAGE_KEY = "bd_theme";

// Fired whenever the theme changes (explicit toggle or a system preference
// change while no explicit choice is stored), so subscribers can re-read it.
export const THEME_CHANGE_EVENT = "bd-theme-changed";

export function getEffectiveTheme(): Theme {
  if (typeof document === "undefined") return "light";
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit === "light" || explicit === "dark") return explicit;
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function setTheme(theme: Theme): void {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(STORAGE_KEY, theme);
  window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
}
