"use strict";

var menuBtn = document.getElementById("Hamburger-menu-btn");
var sidebar = document.getElementById("sidebar");
var closeBtn = document.getElementById("close-btn");
menuBtn.addEventListener("click", function () {
  return sidebar.classList.toggle("active");
});
closeBtn.addEventListener("click", function () {
  return sidebar.classList.remove("active");
});
//# sourceMappingURL=student_base.dev.js.map
