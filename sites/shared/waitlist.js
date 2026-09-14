/**
 * Static waitlist stub — stores email locally for demo; replace with your API endpoint.
 */
(function () {
  const form = document.querySelector("[data-waitlist-form]");
  if (!form) return;

  const success = document.querySelector("[data-waitlist-success]");
  const storageKey = form.getAttribute("data-storage-key") || "waitlist:default";

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const input = form.querySelector('input[type="email"]');
    const email = (input && input.value ? input.value : "").trim().toLowerCase();
    if (!email || !input.checkValidity()) {
      input.reportValidity();
      return;
    }

    try {
      const existing = JSON.parse(localStorage.getItem(storageKey) || "[]");
      if (!existing.includes(email)) {
        existing.push(email);
        localStorage.setItem(storageKey, JSON.stringify(existing));
      }
    } catch {
      /* ignore quota / private mode */
    }

    form.hidden = true;
    if (success) {
      success.classList.add("is-visible");
      success.setAttribute("tabindex", "-1");
      success.focus();
    }
  });
})();
