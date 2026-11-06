
from data.libraries import LIBRARIES


# Current simulated environment state
# This is shared by the simulator and the intelligent agent.

POPULATION = {}


def initialize_population():
    """Initialize occupancy and equipment status for both libraries."""

    for library_id, library in LIBRARIES.items():

        POPULATION[library_id] = {
            "resources": {},
            "printers": {
                "status": "available"
            }
        }

        for category, locations in library["resources"].items():

            POPULATION[library_id]["resources"][category] = {}

            for location in locations:

                POPULATION[library_id]["resources"][category][location["id"]] = {
                    "occupied": 0,
                    "available": location["capacity"]
                }


def update_occupancy(library_id, category, location_id, occupied):
    """Update the number of occupied resources."""

    if library_id not in POPULATION:
        return False, "Library not found."

    if category not in POPULATION[library_id]["resources"]:
        return False, "Resource category not found."

    location = POPULATION[library_id]["resources"][category].get(location_id)

    if location is None:
        return False, "Location not found."

    capacity = next(
        item["capacity"]
        for item in LIBRARIES[library_id]["resources"][category]
        if item["id"] == location_id
    )

    if not isinstance(occupied, int) or isinstance(occupied, bool):
        return False, "Occupancy must be a whole number."

    if occupied < 0 or occupied > capacity:
        return False, f"Occupancy must be between 0 and {capacity}."

    location["occupied"] = occupied
    location["available"] = capacity - occupied

    return True, "Occupancy updated successfully."


def update_printer_status(library_id, status):
    """Update the simulated printer status."""

    if library_id not in POPULATION:
        return False, "Library not found."

    allowed_statuses = ["available", "busy", "offline"]

    if status not in allowed_statuses:
        return False, "Invalid printer status."

    POPULATION[library_id]["printers"]["status"] = status

    return True, "Printer status updated successfully."


def update_all_settings(occupancy_updates, printer_updates):
    """Validate all simulation settings, then apply them together."""

    if not isinstance(occupancy_updates, list):
        return False, "Invalid occupancy data."

    if not isinstance(printer_updates, dict):
        return False, "Invalid printer data."

    validated_occupancy = []
    seen_locations = set()

    # Validate all occupancy values without changing the current state.
    for item in occupancy_updates:
        if not isinstance(item, dict):
            return False, "Invalid occupancy entry."

        library_id = item.get("library_id")
        category = item.get("category")
        location_id = item.get("location_id")
        occupied = item.get("occupied")

        if library_id not in LIBRARIES:
            return False, "Invalid library."

        if category not in LIBRARIES[library_id]["resources"]:
            return False, "Invalid resource category."

        location = next(
            (
                resource
                for resource in LIBRARIES[library_id]["resources"][category]
                if resource["id"] == location_id
            ),
            None
        )

        if location is None:
            return False, "Invalid resource location."

        key = (library_id, category, location_id)

        if key in seen_locations:
            return False, "Duplicate resource entry."

        seen_locations.add(key)

        if (
            not isinstance(occupied, int)
            or isinstance(occupied, bool)
            or occupied < 0
            or occupied > location["capacity"]
        ):
            return False, f"Invalid occupancy for {location['name']}."

        validated_occupancy.append(
            (library_id, category, location_id, occupied, location["capacity"])
        )

    # Make sure every resource was included.
    expected_locations = {
        (library_id, category, location["id"])
        for library_id, library in LIBRARIES.items()
        for category, locations in library["resources"].items()
        for location in locations
    }

    if seen_locations != expected_locations:
        return False, "Some library resources are missing from the update."

    # Validate printer statuses.
    if set(printer_updates.keys()) != set(LIBRARIES.keys()):
        return False, "Printer settings are incomplete."

    allowed_statuses = ["available", "busy", "offline"]

    for library_id, status in printer_updates.items():
        if status not in allowed_statuses:
            return False, f"Invalid printer status for {library_id}."

    # All validation passed. Apply the changes.
    for library_id, category, location_id, occupied, capacity in validated_occupancy:
        POPULATION[library_id]["resources"][category][location_id] = {
            "occupied": occupied,
            "available": capacity - occupied
        }

    for library_id, status in printer_updates.items():
        POPULATION[library_id]["printers"]["status"] = status

    return True, "All simulation settings saved successfully."

def get_population():
    """Return the current simulated environment state."""

    return POPULATION


initialize_population()
