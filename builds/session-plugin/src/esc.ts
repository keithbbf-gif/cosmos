// HTML-safe encoding for user/session-derived text returned to hosts that may
// embed tool output in markup (same contract as kdash esc()).

const MAP: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

/** Escape data text before it leaves the plugin envelope. */
export function esc(value: unknown): string {
  return String(value ?? "").replace(/[&<>"']/g, (c) => MAP[c] ?? c);
}
