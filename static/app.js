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

                index = Math.min(
                    index + 1,
                    items.length - 1
                );
            }

            // Arrow up
            else if (e.key === "ArrowUp") {
                e.preventDefault();

                index = Math.max(
                    index - 1,
                    0
                );
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

                item.classList.toggle(
                    "selected",
                    i === index
                );

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

    const watchlistMenus = document.querySelectorAll(
        ".watchlist-menu"
    );

    // Only initialise this functionality on pages
    // that actually contain watchlist menus
    if (watchlistMenus.length) {

        document.addEventListener("click", (event) => {

            const menuButton = event.target.closest(
                ".watchlist-menu-button"
            );


            // -------------------------
            // MENU BUTTON
            // -------------------------

            if (menuButton) {

                event.preventDefault();

                const menu = menuButton.closest(
                    ".watchlist-menu"
                );

                const dropdown = menu.querySelector(
                    ".watchlist-menu-dropdown"
                );


                // Close all other menus
                document
                    .querySelectorAll(
                        ".watchlist-menu-dropdown.open"
                    )
                    .forEach((openMenu) => {

                        if (openMenu !== dropdown) {

                            openMenu.classList.remove("open");

                            const otherButton =
                                openMenu
                                    .closest(".watchlist-menu")
                                    .querySelector(
                                        ".watchlist-menu-button"
                                    );

                            otherButton.setAttribute(
                                "aria-expanded",
                                "false"
                            );

                        }

                    });


                // Toggle current menu
                const isOpen =
                    dropdown.classList.toggle("open");


                menuButton.setAttribute(
                    "aria-expanded",
                    isOpen ? "true" : "false"
                );

                return;
            }


            // -------------------------
            // CLICKED MENU ACTION
            // -------------------------

            const menuAction = event.target.closest(
                ".watchlist-menu-dropdown button"
            );


            if (menuAction) {

                const menu = menuAction.closest(
                    ".watchlist-menu"
                );

                const dropdown = menu.querySelector(
                    ".watchlist-menu-dropdown"
                );

                const button = menu.querySelector(
                    ".watchlist-menu-button"
                );


                dropdown.classList.remove("open");

                button.setAttribute(
                    "aria-expanded",
                    "false"
                );

                return;
            }


            // -------------------------
            // CLICKED OUTSIDE MENU
            // -------------------------

            if (!event.target.closest(".watchlist-menu")) {

                document
                    .querySelectorAll(
                        ".watchlist-menu-dropdown.open"
                    )
                    .forEach((dropdown) => {

                        dropdown.classList.remove("open");

                        const button =
                            dropdown
                                .closest(".watchlist-menu")
                                .querySelector(
                                    ".watchlist-menu-button"
                                );

                        button.setAttribute(
                            "aria-expanded",
                            "false"
                        );

                    });

            }

        });

    }

});