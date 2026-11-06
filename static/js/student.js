
const activityButtons = document.querySelectorAll(".activity-button");
const campusButtons = document.querySelectorAll(".campus-button");

const messageInput = document.getElementById("student-message");
const groupSizeContainer = document.getElementById("group-size-container");
const groupSizeInput = document.getElementById("group-size");

const recommendButton = document.getElementById("recommend-button");
const resultCard = document.getElementById("result-card");
const resultContent = document.getElementById("result-content");

let selectedIntent = null;
let selectedCampus = "both";

const activityMessages = {
    reading: "I want a place to study and read.",
    charging: "I need to charge my device.",
    computer: "I want to use a computer.",
    discussion: "I need a place for group study.",
    printing: "I want to print my documents."
};

// Activity selection with deselection
activityButtons.forEach(button => {
    button.addEventListener("click", () => {

        // Clicking the already selected button deselects it
        if (selectedIntent === button.dataset.intent) {
            selectedIntent = null;
            button.classList.remove("selected");
        } else {
            activityButtons.forEach(item => {
                item.classList.remove("selected");
            });

            button.classList.add("selected");
            selectedIntent = button.dataset.intent;
        }

        groupSizeContainer.classList.toggle(
            "hidden",
            selectedIntent !== "discussion"
        );
    });
});


// Campus selection
campusButtons.forEach(button => {
    button.addEventListener("click", () => {
        campusButtons.forEach(item => item.classList.remove("selected"));

        button.classList.add("selected");
        selectedCampus = button.dataset.campus;
    });
});

// Create recommendation result safely
function displayResult(result) {
    resultContent.replaceChildren();

    const message = document.createElement("p");
    message.textContent = result.message;
    resultContent.appendChild(message);

    if (result.success) {
        const recommendation = result.recommendation;

        const location = document.createElement("h3");
        location.textContent = recommendation.location;

        const library = document.createElement("p");
        library.textContent = recommendation.library_name;

        const availability = document.createElement("p");

        if (result.intent === "printing") {
            availability.textContent = "Printer status: Available";
        } else {
            availability.textContent =
                `Available resources: ${recommendation.available}`;
        }

        resultContent.append(location, library, availability);
    }
}

// Submit recommendation request
recommendButton.addEventListener("click", async () => {
    const customMessage = messageInput.value.trim();

    let message = customMessage;

    if (!message && selectedIntent) {
        message = activityMessages[selectedIntent];
    }

    if (!message) {
        alert("Please select an activity or describe what you need.");
        return;
    }

    const groupSize = Number(groupSizeInput.value);

    if (
        selectedIntent === "discussion" &&
        !customMessage &&
        (!Number.isInteger(groupSize) || groupSize < 1 || groupSize > 20)
    ) {
        alert("Please enter a group size between 1 and 20.");
        return;
    }

    recommendButton.disabled = true;
    recommendButton.textContent = "Finding a location...";

    try {
        const response = await fetch("/api/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                campus: selectedCampus,
                group_size: selectedIntent === "discussion" && !customMessage
                    ? groupSize
                    : 1
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || "Request failed.");
        }

        resultCard.classList.remove("hidden");
        displayResult(result);

    } catch (error) {
        resultCard.classList.remove("hidden");
        resultContent.textContent =
            error.message || "Unable to connect to the server.";

    } finally {
        recommendButton.disabled = false;
        recommendButton.textContent = "Find a Study Space";
    }
});
