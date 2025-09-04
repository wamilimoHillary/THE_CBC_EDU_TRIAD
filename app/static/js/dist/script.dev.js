"use strict";

/*Typewriter*/
document.addEventListener("DOMContentLoaded", function () {
  var textElement = document.getElementById('typing-text');

  if (textElement) {
    // delay between texts in milliseconds
    var type = function type() {
      if (charIndex < texts[textIndex].length) {
        textElement.textContent += texts[textIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, typingSpeed);
      } else {
        setTimeout(erase, delayBetweenTexts);
      }
    };

    var erase = function erase() {
      if (charIndex > 0) {
        textElement.textContent = texts[textIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingSpeed);
      } else {
        textIndex = (textIndex + 1) % texts.length;
        setTimeout(type, typingSpeed);
      }
    };

    var texts = ["Welcome to CBC-EDU Triad 🎓", "Discover the power of CBC-driven learning 📘", "Map Competencies. Submit Projects. Get Feedback.", "Students: Upload your innovation projects with ease!", "Teachers: Assess with rubrics aligned to CBC standards.", "Parents: Give feedback and stay engaged in your child's learning.", "Track growth, showcase skills, and grow together 🚀"];
    var textIndex = 0;
    var charIndex = 0;
    var typingSpeed = 80; // typing speed in milliseconds

    var erasingSpeed = 5; // erasing speed in milliseconds

    var delayBetweenTexts = 2000;
    setTimeout(type, typingSpeed);
  } else {
    console.error('Element with id "typing-text" not found');
  }
});
/* START UP LOADER*/
// Wait for 3 seconds (loading effect), then show content

setTimeout(function () {
  document.getElementById("loader").style.display = "none"; // Hide loader

  document.getElementById("content").classList.remove("hidden"); // Show content
}, 400);
/*SIDEBAR TOGGLING */

document.addEventListener("DOMContentLoaded", function () {
  var menuBtn = document.getElementById("Hamburger-menu-btn");
  var sidebar = document.querySelector(".sidebar");
  var closeBtn = document.createElement("button");
  closeBtn.innerHTML = "&times;";
  closeBtn.classList.add("close-btn");
  sidebar.prepend(closeBtn);
  menuBtn.addEventListener("click", function () {
    sidebar.classList.add("show-sidebar");
  });
  closeBtn.addEventListener("click", function () {
    sidebar.classList.remove("show-sidebar");
  });
});
/* DARKMODE*/

document.addEventListener("DOMContentLoaded", function () {
  var toggleSwitch = document.getElementById("toggle-dark-mode");
  var body = document.body; // Check for dark mode preference in localStorage

  if (localStorage.getItem("darkMode") === "enabled") {
    body.classList.add("dark-mode");
    toggleSwitch.checked = true;
  } // Toggle dark mode and store preference


  toggleSwitch.addEventListener("change", function () {
    if (this.checked) {
      body.classList.add("dark-mode");
      localStorage.setItem("darkMode", "enabled");
    } else {
      body.classList.remove("dark-mode");
      localStorage.setItem("darkMode", "disabled");
    }
  });
});
/*SHAKE THE HUMBURGER */

document.addEventListener("DOMContentLoaded", function () {
  function shakeMenu() {
    var menu = document.querySelector(".Hamburger-menu-btn");
    menu.classList.add("shake");
    setTimeout(function () {
      menu.classList.remove("shake");
    }, 500); // Remove shake after animation duration (0.5s)

    setTimeout(shakeMenu, 3500); // Restart shake after 3-second pause
  }

  setTimeout(shakeMenu, 3000); // Start shaking after initial 3 seconds
}); // Admin dashboard link functionality hide the admin form 

document.addEventListener("DOMContentLoaded", function () {
  var tapCount = 0; // Get the admin button and its data-url attribute

  var adminButton = document.getElementById("hidden_admin_function");
  var adminLoginUrl = adminButton.getAttribute('data-url'); // Get the URL from the data attribute

  adminButton.addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default link behavior

    tapCount++;

    if (tapCount === 4) {
      // Redirect to the admin login page using the Flask-generated URL
      window.location.href = adminLoginUrl;
    } // Reset the tap count after 2 seconds of inactivity


    setTimeout(function () {
      tapCount = 0;
    }, 2000);
  });
});
//# sourceMappingURL=script.dev.js.map
