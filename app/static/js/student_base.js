const menuBtn = document.getElementById("Hamburger-menu-btn");
const sidebar = document.getElementById("sidebar");
const closeBtn = document.getElementById("close-btn");
menuBtn.addEventListener("click", () => sidebar.classList.toggle("active"));
closeBtn.addEventListener("click", () => sidebar.classList.remove("active"));