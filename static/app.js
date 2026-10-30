document.addEventListener("DOMContentLoaded", () => {
  // ---------- SEARCH AUTOCOMPLETE ----------

  const input = document.getElementById("search");
  const autocomplete = document.getElementById("autocomplete");

  let index = -1;

  // Only run search keyboard functionality if search exists
  if (input && autocomplete) {
    const form = input.closest("form");

    document.addEventListener("keydown", (e) => {
      const items = document.querySelectorAll(".autocomplete-item");

      if (!items.length) {
        return;
      }

      // Arrow down
      if (e.key === "ArrowDown") {
        e.preventDefault();

        index = Math.min(index + 1, items.length - 1);
      }

      // Arrow up
      else if (e.key === "ArrowUp") {
        e.preventDefault();

        index = Math.max(index - 1, 0);
      }

      // Enter on highlighted suggestion
      else if (e.key === "Enter" && index >= 0) {
        e.preventDefault();

        autocomplete.style.display = "none";
        input.blur();

        items[index].click();

        return;
      }

      // Update selected item
      items.forEach((item, i) => {
        item.classList.toggle("selected", i === index);
      });
    });

    // Hide autocomplete when normal search is submitted
    if (form) {
      form.addEventListener("submit", () => {
        autocomplete.style.display = "none";

        index = -1;
      });
    }
  }

  // ---------- WATCHLIST ACTION MENUS ----------

  const watchlistMenus = document.querySelectorAll(".watchlist-menu");

  // Only initialise this functionality on pages
  // that actually contain watchlist menus
  if (watchlistMenus.length) {
    document.addEventListener("click", (event) => {
      const menuButton = event.target.closest(".watchlist-menu-button");

      // -------------------------
      // MENU BUTTON
      // -------------------------

      if (menuButton) {
        event.preventDefault();

        const menu = menuButton.closest(".watchlist-menu");

        const dropdown = menu.querySelector(".watchlist-menu-dropdown");

        // Close all other menus
        document
          .querySelectorAll(".watchlist-menu-dropdown.open")
          .forEach((openMenu) => {
            if (openMenu !== dropdown) {
              openMenu.classList.remove("open");

              const otherButton = openMenu
                .closest(".watchlist-menu")
                .querySelector(".watchlist-menu-button");

              otherButton.setAttribute("aria-expanded", "false");
            }
          });

        // Toggle current menu
        const isOpen = dropdown.classList.toggle("open");

        menuButton.setAttribute("aria-expanded", isOpen ? "true" : "false");

        return;
      }

      // -------------------------
      // CLICKED MENU ACTION
      // -------------------------

      const menuAction = event.target.closest(
        ".watchlist-menu-dropdown button",
      );

      if (menuAction) {
        const menu = menuAction.closest(".watchlist-menu");

        const dropdown = menu.querySelector(".watchlist-menu-dropdown");

        const button = menu.querySelector(".watchlist-menu-button");

        dropdown.classList.remove("open");

        button.setAttribute("aria-expanded", "false");

        return;
      }

      // -------------------------
      // CLICKED OUTSIDE MENU
      // -------------------------

      if (!event.target.closest(".watchlist-menu")) {
        document
          .querySelectorAll(".watchlist-menu-dropdown.open")
          .forEach((dropdown) => {
            dropdown.classList.remove("open");

            const button = dropdown
              .closest(".watchlist-menu")
              .querySelector(".watchlist-menu-button");

            button.setAttribute("aria-expanded", "false");
          });
      }
    });
  }
  // ---------- AUTH FORM SUBMISSIONS ----------

  const authForms = document.querySelectorAll(".auth-form");

  if (authForms.length) {
    authForms.forEach((form) => {
      form.addEventListener("submit", () => {
        const button = form.querySelector("button[type='submit']");

        if (!button) {
          return;
        }

        // Prevent accidental double submissions
        button.disabled = true;

        // Show immediate feedback
        const buttonText = button.textContent.trim();

        if (buttonText === "Log in") {
          button.textContent = "Logging in...";
        } else if (buttonText === "Send reset link") {
          button.textContent = "Sending...";
        } else if (buttonText === "Reset password") {
          button.textContent = "Resetting...";
        }
      });
    });
  }

  /* ---------- PASSWORD VISIBILITY TOGGLE ---------- */

  document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const inputId = button.getAttribute("aria-controls");
      const passwordInput = document.getElementById(inputId);

      if (!passwordInput) return;

      const shouldShow = passwordInput.type === "password";

      passwordInput.type = shouldShow ? "text" : "password";

      button.innerHTML = shouldShow
        ? `
        <svg class="password-eye-icon"
          xmlns="http://www.w3.org/2000/svg"
          width="22" height="22" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
          aria-hidden="true">
          <path d="M3 3l18 18" />
          <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
          <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a15.8 15.8 0 0 1-4 4.8" />
          <path d="M6.6 6.6C3.6 8.5 2 12 2 12s3.6 7 10 7c1.5 0 2.8-.3 4-.9" />
        </svg>
      `
        : `
        <svg class="password-eye-icon"
          xmlns="http://www.w3.org/2000/svg"
          width="22" height="22" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
          aria-hidden="true">
          <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      `;

      button.setAttribute(
        "aria-label",
        shouldShow ? "Hide password" : "Show password",
      );
      button.setAttribute("aria-pressed", String(shouldShow));
    });
  });
});
