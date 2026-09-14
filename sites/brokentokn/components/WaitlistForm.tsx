"use client";

import { FormEvent, useState } from "react";

type Status = "idle" | "submitting" | "success" | "error";

const STORAGE_KEY = "brokentokn_waitlist_v1";

export function WaitlistForm({ compact = false }: { compact?: boolean }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = email.trim().toLowerCase();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setStatus("error");
      setMessage("Enter a valid email address.");
      return;
    }

    setStatus("submitting");
    setMessage("");

    try {
      const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]") as string[];
      if (!existing.includes(trimmed)) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify([...existing, trimmed]));
      }
      setStatus("success");
      setMessage("You're on the list. We'll reach out when invites open.");
      setEmail("");
    } catch {
      setStatus("error");
      setMessage("Something went wrong. Try again or email hello@brokentokn.com.");
    }
  }

  return (
    <div className={compact ? "waitlist waitlist--compact" : "waitlist"}>
      <form className="waitlist__form" onSubmit={handleSubmit} noValidate>
        <label className="visually-hidden" htmlFor="waitlist-email">
          Email
        </label>
        <input
          id="waitlist-email"
          className="field waitlist__input"
          type="email"
          name="email"
          autoComplete="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={status === "submitting" || status === "success"}
          required
        />
        <button
          type="submit"
          className="btn btn--primary waitlist__submit"
          disabled={status === "submitting" || status === "success"}
        >
          {status === "submitting" ? "Joining…" : "Join waitlist"}
        </button>
      </form>
      {message ? (
        <p
          className={`waitlist__message waitlist__message--${status === "error" ? "error" : "ok"}`}
          role="status"
        >
          {message}
        </p>
      ) : null}
      {!compact && (
        <p className="waitlist__note">
          No spam. One update when your invite is ready. Wire your own endpoint in{" "}
          <code>components/WaitlistForm.tsx</code> before production.
        </p>
      )}
    </div>
  );
}
