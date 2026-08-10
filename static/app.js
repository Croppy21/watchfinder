document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("search");
    const form = input.closest("form");
    const autocomplete = document.getElementById("autocomplete");

    let index = -1;

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

});