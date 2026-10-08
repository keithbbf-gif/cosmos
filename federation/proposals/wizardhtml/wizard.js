"use strict";

// The key is whatever the person pastes. This file does not read a
// password manager or a browser profile, and it does not drive a vendor login.
(function () {
  const SETUP = "/api/v1/dayone/setup";
  const CHAT = "/api/v1/dayone/chat";

  const form = document.getElementById("setup-form");
  const keyInput = document.getElementById("key");
  const tlsInput = document.getElementById("tls");
  const tlsRow = document.getElementById("tls-row");
  const remoteInput = document.getElementById("bind-remote");
  const loopbackInput = document.getElementById("bind-loopback");
  const wizard = document.getElementById("wizard");
  const chat = document.getElementById("chat");
  const setupError = document.getElementById("setup-error");
  const chatForm = document.getElementById("chat-form");
  const draft = document.getElementById("draft");
  const transcript = document.getElementById("transcript");
  const emptyNote = document.getElementById("empty-note");
  const chatError = document.getElementById("chat-error");

  function show(el, message) {
    if (!el) {
      return;
    }
    el.hidden = false;
    el.textContent = message;
  }

  function hide(el) {
    if (!el) {
      return;
    }
    el.hidden = true;
    el.textContent = "";
  }

  function syncBind() {
    if (!remoteInput || !tlsInput || !tlsRow) {
      return;
    }
    const remote = remoteInput.checked === true;
    tlsRow.classList.toggle("show", remote);
    tlsInput.required = remote;
    tlsInput.disabled = !remote;
    if (!remote) {
      tlsInput.checked = false;
    }
  }

  function encodeForm(source) {
    const parts = [];
    const data = new FormData(source);
    data.forEach((entry, field) => {
      parts.push(encodeURIComponent(field) + "=" + encodeURIComponent(String(entry)));
    });
    return parts.join("&");
  }

  function appendLine(role, text, micros) {
    if (!transcript) {
      return;
    }
    if (emptyNote) {
      emptyNote.hidden = true;
    }
    const item = document.createElement("li");
    item.className = role === "assistant" ? "assistant" : "user";
    const who = document.createElement("span");
    who.className = "who";
    who.textContent = role === "assistant" ? "Agent" : "You";
    const body = document.createElement("p");
    body.textContent = text;
    item.appendChild(who);
    item.appendChild(body);
    if (typeof micros === "number" && Number.isFinite(micros)) {
      const cost = document.createElement("span");
      cost.className = "cost";
      cost.textContent = String(micros) + " micros";
      item.appendChild(cost);
    }
    transcript.appendChild(item);
  }

  if (remoteInput) {
    remoteInput.addEventListener("change", syncBind);
  }
  if (loopbackInput) {
    loopbackInput.addEventListener("change", syncBind);
  }
  syncBind();

  if (form && keyInput) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      hide(setupError);
      if (remoteInput && remoteInput.checked && tlsInput && !tlsInput.checked) {
        show(setupError, "Remote requires TLS.");
        return;
      }
      keyInput.value = keyInput.value.trim();
      if (keyInput.value === "") {
        show(setupError, "A key is required.");
        return;
      }
      const encoded = encodeForm(form);
      // Clear the control now. The secret would otherwise stay on screen and
      // in the DOM after submit, including in a later copy of this page.
      keyInput.value = "";
      // Do not keep a second copy in localStorage or sessionStorage, and do
      // not move the key onto the query string. Those copies outlive the
      // submit. This script never writes browser storage and never rewrites
      // the address. The encoded body is the only copy, and it leaves with
      // this POST.
      fetch(SETUP, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: encoded,
      })
        .then((response) => {
          keyInput.value = "";
          if (!response.ok) {
            show(setupError, "Setup was refused.");
            return;
          }
          if (wizard) {
            wizard.hidden = true;
          }
          if (chat) {
            chat.hidden = false;
          }
          if (draft) {
            draft.focus();
          }
        })
        .catch(() => {
          keyInput.value = "";
          show(setupError, "Setup was refused.");
        });
    });
  }

  if (chatForm && draft) {
    chatForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const text = draft.value.trim();
      if (text === "") {
        return;
      }
      hide(chatError);
      appendLine("user", text);
      draft.value = "";
      fetch(CHAT, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: text }),
      })
        .then((response) => {
          if (!response.ok) {
            show(chatError, "The turn was refused.");
            return null;
          }
          return response.json();
        })
        .then((reply) => {
          if (!reply || typeof reply.text !== "string" || reply.text === "") {
            return;
          }
          const role = reply.role === "user" ? "user" : "assistant";
          appendLine(role, reply.text, reply.usd_micros);
        })
        .catch(() => {
          show(chatError, "The turn was refused.");
        });
    });
  }
})();
