document.addEventListener("DOMContentLoaded", () => {
    console.log("DV Dashboard initialized");

    initializeTooltips();
    initializeCopyButtons();
    initializeDropdowns();
});

function initializeCopyButtons() {
    document.querySelectorAll("[data-copy]").forEach((button) => {
        button.addEventListener("click", async () => {
            const text = button.dataset.copy;

            try {
                await navigator.clipboard.writeText(text);

                const original = button.innerHTML;

                button.innerHTML = `
                    <i class="ri-check-line"></i>
                    Copied
                `;

                setTimeout(() => {
                    button.innerHTML = original;
                }, 2000);
            } catch (err) {
                console.error(err);
            }
        });
    });
}

function initializeDropdowns() {
    document.querySelectorAll("[data-dropdown-toggle]").forEach((trigger) => {
        trigger.addEventListener("click", () => {
            const id = trigger.dataset.dropdownToggle;

            const menu = document.getElementById(id);

            if (!menu) return;

            menu.classList.toggle("hidden");
        });
    });

    document.addEventListener("click", (e) => {
        const toggle = e.target.closest("[data-dropdown-toggle]");

        if (toggle) return;

        document.querySelectorAll("[id]").forEach((el) => {
            if (el.classList.contains("dropdown")) {
                el.classList.add("hidden");
            }
        });
    });
}

/**
 * Future tooltip support
 */
function initializeTooltips() {
    document.querySelectorAll("[data-tooltip]").forEach((element) => {
        element.setAttribute("title", element.dataset.tooltip);
    });
}

/**
 * Toast helper
 */
function showToast(message, type = "info") {
    const toast = document.createElement("div");

    toast.className = `
        fixed
        bottom-6
        right-6
        glass
        px-4
        py-3
        z-50
        shadow-lg
    `;

    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

window.showToast = showToast;
