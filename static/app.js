const input = document.getElementById("search");
const box = document.getElementById("autocomplete");

let index = -1;

document.addEventListener("keydown", (e) => {

    const items = document.querySelectorAll(".autocomplete-item");

    if (!items.length) return;

    if (e.key === "ArrowDown") {
        index = Math.min(index + 1, items.length - 1);
    }

    if (e.key === "ArrowUp") {
        index = Math.max(index - 1, 0);
    }

    if (e.key === "Enter" && index >= 0) {
        items[index].click();
    }

    items.forEach((el, i) => {
        el.classList.toggle("selected", i === index);
    });

});