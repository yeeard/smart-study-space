
from data.libraries import LIBRARIES
from simulator.population import get_population


def identify_intent(message):
    """Identify what the student wants to do."""
    message = message.lower().strip()

    # Printing requests
    if any(word in message for word in [
        "print", "printer", "printing"
    ]):
        return "printing"

    # Charging requests
    if any(word in message for word in [
        "charge", "charging", "outlet", "power outlet"
    ]):
        return "charging"

    # Group activities
    if any(phrase in message for phrase in [
        "group study",
        "study with friends",
        "study with my friends",
        "study together",
        "group work",
        "group meeting",
        "discuss",
        "discussion",
        "collaborate"
    ]):
        return "discussion"

    # Computer requests
    if any(word in message for word in [
        "computer", "computers", "pc", "research room"
    ]):
        return "computer"

    # Laptop work: recommend a reading/study area
    if any(phrase in message for phrase in [
        "work on my laptop", "use my laptop",
        "work on laptop", "use laptop",
        "laptop work", "bring my laptop"
    ]):
        return "reading"

    # Individual studying and reading
    if any(word in message for word in [
        "study", "read", "reading", "review",
        "quiet place", "quiet area"
    ]):
        return "reading"

    return "unknown"


def recommend_location(intent, campus="both", group_size=1):
    """Recommend the most suitable available library location."""

    if intent not in [
        "printing", "charging", "computer",
        "discussion", "reading"
    ]:
        return {
            "success": False,
            "message": "I couldn't identify a suitable resource for your request."
        }

    if campus != "both" and campus not in LIBRARIES:
        return {
            "success": False,
            "message": "Invalid campus selection."
        }

    if (
        not isinstance(group_size, int)
        or isinstance(group_size, bool)
        or group_size < 1
        or group_size > 20
    ):
        return {
            "success": False,
            "message": "Group size must be a whole number between 1 and 20."
        }

    population = get_population()
    candidates = []

    if campus == "both":
        selected_libraries = LIBRARIES.keys()
    else:
        selected_libraries = [campus]

    # Check printer availability
    if intent == "printing":
        for library_id in selected_libraries:
            printer_status = population[library_id]["printers"]["status"]

            if printer_status == "available":
                candidates.append({
                    "library_id": library_id,
                    "library_name": LIBRARIES[library_id]["name"],
                    "location": "Research Room",
                    "available": 1
                })

    # Check other resources
    else:
        for library_id in selected_libraries:
            locations = LIBRARIES[library_id]["resources"].get(intent, [])

            for location in locations:
                current = population[library_id]["resources"][intent][location["id"]]
                available = current["available"]

                required = group_size if intent == "discussion" else 1

                if available >= required:
                    candidates.append({
                        "library_id": library_id,
                        "library_name": LIBRARIES[library_id]["name"],
                        "location_id": location["id"],
                        "location": location["name"],
                        "available": available
                    })

    if not candidates:
        return {
            "success": False,
            "message": "Sorry, no suitable location is currently available."
        }

    # Select the location with the most available resources
    best_location = max(
        candidates,
        key=lambda item: item["available"]
    )

    return {
        "success": True,
        "recommendation": best_location,
        "message": (
            f"I recommend {best_location['location']} "
            f"at {best_location['library_name']}."
        )
    }
