/*Typewriter*/
document.addEventListener("DOMContentLoaded", function () {
    const textElement = document.getElementById('typing-text');
    if (textElement) {
        const texts = [
            "Welcome to CBC-EDU Triad 🎓",
            "Discover the power of CBC-driven learning 📘",
            "Map Competencies. Submit Projects. Get Feedback.",
            "Students: Upload your innovation projects with ease!",
            "Teachers: Assess with rubrics aligned to CBC standards.",
            "Parents: Give feedback and stay engaged in your child's learning.",
            "Track growth, showcase skills, and grow together 🚀"
        ];
        

        let textIndex = 0;
        let charIndex = 0;
        const typingSpeed = 80; // typing speed in milliseconds
        const erasingSpeed = 5; // erasing speed in milliseconds
        const delayBetweenTexts = 2000; // delay between texts in milliseconds

        function type() {
            if (charIndex < texts[textIndex].length) {
                textElement.textContent += texts[textIndex].charAt(charIndex);
                charIndex++;
                setTimeout(type, typingSpeed);
            } else {
                setTimeout(erase, delayBetweenTexts);
            }
        }

        function erase() {
            if (charIndex > 0) {
                textElement.textContent = texts[textIndex].substring(0, charIndex - 1);
                charIndex--;
                setTimeout(erase, erasingSpeed);
            } else {
                textIndex = (textIndex + 1) % texts.length;
                setTimeout(type, typingSpeed);
            }
        }

        setTimeout(type, typingSpeed);
    } else {
        console.error('Element with id "typing-text" not found');
    }
});


/* START UP LOADER*/
// Wait for 3 seconds (loading effect), then show content
setTimeout(() => {
    document.getElementById("loader").style.display = "none";  // Hide loader
    document.getElementById("content").classList.remove("hidden");  // Show content
}, 400);

/*SIDEBAR TOGGLING */
document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = document.getElementById("Hamburger-menu-btn");
    const sidebar = document.querySelector(".sidebar");
    const closeBtn = document.createElement("button");

    closeBtn.innerHTML = "&times;"; 
    closeBtn.classList.add("close-btn");
    sidebar.prepend(closeBtn); 

    menuBtn.addEventListener("click", () => {
        sidebar.classList.add("show-sidebar");
    });

    closeBtn.addEventListener("click", () => {
        sidebar.classList.remove("show-sidebar");
    });
});

/* DARKMODE*/
document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("toggle-dark-mode");
    const body = document.body;

    // Check for dark mode preference in localStorage
    if (localStorage.getItem("darkMode") === "enabled") {
        body.classList.add("dark-mode");
        toggleSwitch.checked = true;
    }

    // Toggle dark mode and store preference
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
document.addEventListener("DOMContentLoaded", function() {
    function shakeMenu() {
        const menu = document.querySelector(".Hamburger-menu-btn");
        menu.classList.add("shake");

        setTimeout(() => {
            menu.classList.remove("shake");
        }, 500); // Remove shake after animation duration (0.5s)

        setTimeout(shakeMenu, 3500); // Restart shake after 3-second pause
    }

    setTimeout(shakeMenu, 3000); // Start shaking after initial 3 seconds
});


// Admin dashboard link functionality hide the admin form 
document.addEventListener("DOMContentLoaded", () => {
    let tapCount = 0;
    // Get the admin button and its data-url attribute
    const adminButton = document.getElementById("hidden_admin_function");
    const adminLoginUrl = adminButton.getAttribute('data-url'); // Get the URL from the data attribute
    
    adminButton.addEventListener("click", (event) => {
        event.preventDefault(); // Prevent default link behavior
        tapCount++;

        if (tapCount === 4) {
            // Redirect to the admin login page using the Flask-generated URL
            window.location.href = adminLoginUrl;
        }

        // Reset the tap count after 2 seconds of inactivity
        setTimeout(() => {
            tapCount = 0;
        }, 2000);
    });
});