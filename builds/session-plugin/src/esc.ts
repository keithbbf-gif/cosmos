// Data-text escape. Session titles, turn text, excerpts and other host-rendered
// fields go through esc() before they enter a result. Structural fields
// (schema, kind, id, sha) are not data text.

export function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Missing text stays null (empty = explicit). A string is escaped. */
export function escText(value: unknown): string | null {
  return typeof value === "string" ? esc(value) : null;
}
