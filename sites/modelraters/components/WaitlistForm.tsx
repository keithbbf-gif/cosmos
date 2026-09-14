"use client";

import { useState } from "react";
import { site } from "@/lib/site";

type Status = "idle" | "submitted";

export function WaitlistForm() {
  const [status, setStatus] = useState<Status>("idle");

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const endpoint = process.env.NEXT_PUBLIC_WAITLIST_ENDPOINT;
    if (endpoint) {
      const form = e.currentTarget;
      const data = new FormData(form);
      void fetch(endpoint, { method: "POST", body: data }).finally(() => {
        setStatus("submitted");
        form.reset();
      });
      return;
    }
    setStatus("submitted");
    e.currentTarget.reset();
  }

  if (status === "submitted") {
    return (
      <div className="card" role="status">
        <p className="eyebrow">Thank you</p>
        <p style={{ margin: "0.5rem 0 0", fontSize: "1.125rem" }}>
          We received your request. We will be in touch when access opens.
        </p>
        <p className="muted" style={{ marginTop: "1rem", fontSize: "0.875rem" }}>
          Prefer email? Write to{" "}
          <a href={`mailto:${site.contactEmail}`}>{site.contactEmail}</a>.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="card" noValidate>
      <p className="eyebrow">Request access</p>
      <p className="muted" style={{ marginTop: "0.5rem", marginBottom: "1.25rem", fontSize: "0.9375rem" }}>
        Join the waitlist. No spam — early access and product updates only.
      </p>
      <div className="form-field">
        <label htmlFor="waitlist-name">Name</label>
        <input id="waitlist-name" name="name" type="text" autoComplete="name" required />
      </div>
      <div className="form-field">
        <label htmlFor="waitlist-email">Work email</label>
        <input id="waitlist-email" name="email" type="email" autoComplete="email" required />
      </div>
      <div className="form-field">
        <label htmlFor="waitlist-note">What are you comparing? (optional)</label>
        <textarea id="waitlist-note" name="note" placeholder="Models, use cases, team size…" />
      </div>
      <button type="submit" className="btn" style={{ width: "100%", marginTop: "0.5rem" }}>
        Join waitlist
      </button>
      <p className="muted" style={{ marginTop: "1rem", fontSize: "0.75rem", lineHeight: 1.5 }}>
        This form is a shell until you connect a provider at deploy time (
        <code style={{ fontSize: "0.7rem" }}>NEXT_PUBLIC_WAITLIST_ENDPOINT</code>
        ). Submissions are not stored in this repository.
      </p>
    </form>
  );
}
