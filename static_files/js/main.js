document.addEventListener("DOMContentLoaded", function () {
  const toggleDiv = document.querySelector(".user__detail__mobile");
  const toggleBtn = document.querySelector(".nav__bar__btn");

  toggleBtn.addEventListener("click", function () {
    // Toggle visibility based on computed style
    if (getComputedStyle(toggleDiv).display === "none") {
      toggleDiv.style.display = "block";
    } else {
      toggleDiv.style.display = "none";
    }
  });
});
