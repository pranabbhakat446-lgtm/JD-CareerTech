/* =========================================================
   CAREER & INTERNSHIP NETWORK
   MAIN JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("Career & Internship Network loaded successfully.");

    /* =====================================================
       BUTTON CLICK ANIMATION
       ===================================================== */

    const buttons = document.querySelectorAll("a, button");

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {

            button.style.transform = "scale(0.97)";

            setTimeout(function () {
                button.style.transform = "";
            }, 120);

        });

    });


    /* =====================================================
       INTERNSHIP SEARCH
       ===================================================== */

    const searchInput = document.querySelector(".search-input");
    const locationFilter = document.querySelector(".filter-select");
    const internshipCards = document.querySelectorAll(".internship-card");

    function filterInternships() {

        if (!searchInput || !locationFilter) {
            return;
        }

        const searchText = searchInput.value.toLowerCase().trim();
        const selectedLocation = locationFilter.value.toLowerCase();

        internshipCards.forEach(function (card) {

            const cardText = card.innerText.toLowerCase();

            const matchesSearch =
                searchText === "" ||
                cardText.includes(searchText);

            const matchesLocation =
                selectedLocation === "" ||
                cardText.includes(selectedLocation);

            if (matchesSearch && matchesLocation) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }

        });

    }

    if (searchInput) {
        searchInput.addEventListener("input", filterInternships);
    }

    if (locationFilter) {
        locationFilter.addEventListener("change", filterInternships);
    }


    /* =====================================================
       PASSWORD SHOW / HIDE
       ===================================================== */

    const passwordInputs = document.querySelectorAll(
        'input[type="password"]'
    );

    passwordInputs.forEach(function (input) {

        const parent = input.parentElement;

        if (!parent) {
            return;
        }

        const eyeIcon = document.createElement("i");

        eyeIcon.className = "fa-solid fa-eye password-toggle";

        eyeIcon.style.position = "absolute";
        eyeIcon.style.right = "15px";
        eyeIcon.style.top = "50%";
        eyeIcon.style.transform = "translateY(-50%)";
        eyeIcon.style.cursor = "pointer";
        eyeIcon.style.color = "#8a98aa";

        parent.appendChild(eyeIcon);

        eyeIcon.addEventListener("click", function () {

            if (input.type === "password") {

                input.type = "text";
                eyeIcon.className = "fa-solid fa-eye-slash password-toggle";

            } else {

                input.type = "password";
                eyeIcon.className = "fa-solid fa-eye password-toggle";

            }

        });

    });


    /* =====================================================
       FORM SUBMIT LOADING EFFECT
       ===================================================== */

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector('button[type="submit"]');

            if (submitButton) {

                submitButton.dataset.originalText =
                    submitButton.innerText;

                submitButton.innerText = "Please wait...";

                submitButton.disabled = true;

            }

        });

    });


    /* =====================================================
       FADE-IN ANIMATION
       ===================================================== */

    const animatedCards = document.querySelectorAll(
        ".feature-card, .internship-card, .career-card, .stat-card"
    );

    animatedCards.forEach(function (card, index) {

        card.style.opacity = "0";
        card.style.transform = "translateY(15px)";

        setTimeout(function () {

            card.style.transition =
                "opacity 0.5s ease, transform 0.5s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 80);

    });


    /* =====================================================
       CURRENT YEAR IN FOOTER
       ===================================================== */

    const yearElements =
        document.querySelectorAll(".current-year");

    yearElements.forEach(function (element) {
        element.innerText = new Date().getFullYear();
    });

    /* =====================================================
       MOBILE MENU TOGGLE
       ===================================================== */

    const mobileMenuBtn =
        document.getElementById("mobileMenuBtn");

    const mobileNav =
        document.getElementById("mobileNav");

    if (mobileMenuBtn && mobileNav) {

        mobileMenuBtn.addEventListener("click", function () {

            mobileNav.classList.toggle("show");

            if (mobileNav.classList.contains("show")) {

                mobileMenuBtn.innerHTML =
                    '<i class="fa-solid fa-xmark"></i>';

                mobileMenuBtn.setAttribute(
                    "aria-label",
                    "Close Menu"
                );

            } else {

                mobileMenuBtn.innerHTML =
                    '<i class="fa-solid fa-bars"></i>';

                mobileMenuBtn.setAttribute(
                    "aria-label",
                    "Open Menu"
                );

            }

        });


        /* Close menu after selecting a mobile link */

        const mobileLinks =
            mobileNav.querySelectorAll("a");

        mobileLinks.forEach(function (link) {

            link.addEventListener("click", function () {

                mobileNav.classList.remove("show");

                mobileMenuBtn.innerHTML =
                    '<i class="fa-solid fa-bars"></i>';

                mobileMenuBtn.setAttribute(
                    "aria-label",
                    "Open Menu"
                );

            });

        });

    }

});
