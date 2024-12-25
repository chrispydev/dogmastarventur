document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.querySelector(".nav__bar__btn");
    const toggleDiv = document.querySelector(".user__detail__mobile");

    toggleButton.addEventListener("click", function() {
        if (toggleDiv.style.display === "none") {
            toggleDiv.style.display = "block";
        } else {
            toggleDiv.style.display = "none";
        }
    });
});