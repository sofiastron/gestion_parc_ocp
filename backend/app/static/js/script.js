document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const cards = document.querySelectorAll(".card");

    // Recherche dynamique
    searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase();

        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(query)) {
                card.parentElement.style.display = "block";
            } else {
                card.parentElement.style.display = "none";
            }
        });
    });

    // Animation au clic (juste pour l’effet visuel)
    cards.forEach(card => {
        card.addEventListener("click", function () {
            card.classList.add("clicked");
            setTimeout(() => card.classList.remove("clicked"), 200);
        });
    });
});
