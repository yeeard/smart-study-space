
const simulatorContent = document.getElementById("simulator-content");
const saveStatus = document.getElementById("save-status");

async function loadSimulator() {
    try {
        const [libraryResponse, populationResponse] = await Promise.all([
            fetch("/api/libraries"),
            fetch("/api/population")
        ]);

        if (!libraryResponse.ok || !populationResponse.ok) {
            throw new Error("Failed to retrieve library information.");
        }

        const libraries = await libraryResponse.json();
        const population = await populationResponse.json();

        simulatorContent.replaceChildren();

        for (const [libraryId, library] of Object.entries(libraries)) {
            const libraryCard = document.createElement("section");
            libraryCard.className = "library-card";

            const heading = document.createElement("h2");
            heading.textContent = library.name;
            libraryCard.appendChild(heading);

            const floor = document.createElement("p");
            floor.textContent = library.floor;
            libraryCard.appendChild(floor);

            for (const [category, locations] of Object.entries(library.resources)) {
                const categoryHeading = document.createElement("h3");
                categoryHeading.textContent =
                    category.charAt(0).toUpperCase() + category.slice(1);

                libraryCard.appendChild(categoryHeading);

                for (const location of locations) {
                    const current =
                        population[libraryId].resources[category][location.id];

                    const resource = document.createElement("div");
                    resource.className = "resource-control";

                    const name = document.createElement("strong");
                    name.textContent = location.name;

                    const details = document.createElement("p");
                    details.textContent =
                        `${current.occupied} occupied / ${location.capacity} total — ${current.available} available`;

                    const input = document.createElement("input");
                    input.type = "number";
                    input.min = "0";
                    input.max = location.capacity;
                    input.value = current.occupied;
                    input.className = "occupancy-input";

                    input.dataset.library = libraryId;
                    input.dataset.category = category;
                    input.dataset.location = location.id;
                    input.dataset.capacity = location.capacity;

                    input.setAttribute(
                        "aria-label",
                        `Occupancy for ${location.name}`
                    );

                    resource.append(name, details, input);
                    libraryCard.appendChild(resource);
                }
            }

            const printerHeading = document.createElement("h3");
            printerHeading.textContent = "Printer Status";
            libraryCard.appendChild(printerHeading);

            const printerSelect = document.createElement("select");
            printerSelect.className = "printer-select";
            printerSelect.dataset.library = libraryId;

            ["available", "busy", "offline"].forEach(status => {
                const option = document.createElement("option");
                option.value = status;
                option.textContent =
                    status.charAt(0).toUpperCase() + status.slice(1);

                option.selected =
                    population[libraryId].printers.status === status;

                printerSelect.appendChild(option);
            });

            libraryCard.appendChild(printerSelect);
            simulatorContent.appendChild(libraryCard);
        }

        const saveButton = document.createElement("button");
        saveButton.id = "save-all-button";
        saveButton.className = "recommend-button";
        saveButton.textContent = "Save All Changes";

        saveButton.addEventListener("click", saveAllChanges);

        simulatorContent.appendChild(saveButton);

    } catch (error) {
        simulatorContent.textContent =
            "Unable to load the simulator. Please check the server.";

        console.error(error);
    }
}

async function saveAllChanges() {
    const occupancyInputs =
        document.querySelectorAll(".occupancy-input");

    const printerSelects =
        document.querySelectorAll(".printer-select");

    const occupancy = [];

    // Validate every occupancy value before sending anything.
    for (const input of occupancyInputs) {
        const occupied = Number(input.value);
        const capacity = Number(input.dataset.capacity);

        if (
            input.value.trim() === "" ||
            !Number.isInteger(occupied) ||
            occupied < 0 ||
            occupied > capacity
        ) {
            saveStatus.textContent =
                `Invalid occupancy for ${input.dataset.location}. Enter a whole number from 0 to ${capacity}.`;

            saveStatus.className = "save-error";
            input.focus();
            return;
        }

        occupancy.push({
            library_id: input.dataset.library,
            category: input.dataset.category,
            location_id: input.dataset.location,
            occupied: occupied
        });
    }

    const printers = {};

    printerSelects.forEach(select => {
        printers[select.dataset.library] = select.value;
    });

    const saveButton = document.getElementById("save-all-button");

    saveButton.disabled = true;
    saveButton.textContent = "Saving Changes...";

    saveStatus.textContent = "";

    try {
        const response = await fetch("/api/simulation-settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                occupancy: occupancy,
                printers: printers
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Unable to save changes.");
        }

        saveStatus.textContent = "All simulation settings saved successfully.";
        saveStatus.className = "save-success";

        // Refresh the displayed availability using the saved values.
        await loadSimulator();

        saveStatus.textContent = "All simulation settings saved successfully.";
        saveStatus.className = "save-success";

    } catch (error) {
        saveStatus.textContent = error.message;
        saveStatus.className = "save-error";

    } finally {
        const button = document.getElementById("save-all-button");

        if (button) {
            button.disabled = false;
            button.textContent = "Save All Changes";
        }
    }
}

loadSimulator();
