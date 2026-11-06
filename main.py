
from flask import Flask, render_template, request, jsonify

from agent.study_agent import identify_intent, recommend_location
from data.libraries import LIBRARIES
from simulator.population import (
    get_population,
    update_occupancy,
    update_printer_status,
    update_all_settings
)

app = Flask(__name__)


@app.route("/")
def student_page():
    return render_template("student.html")


@app.route("/simulator")
def simulator_page():
    return render_template("simulator.html")


@app.route("/api/libraries", methods=["GET"])
def library_information():
    return jsonify(LIBRARIES)


@app.route("/api/recommend", methods=["POST"])
def get_recommendation():
    data = request.get_json()

    if not data or not isinstance(data.get("message"), str):
        return jsonify({
            "success": False,
            "message": "Please enter a valid request."
        }), 400

    message = data["message"].strip()

    if not message:
        return jsonify({
            "success": False,
            "message": "Please enter what you need."
        }), 400

    intent = identify_intent(message)
    campus = data.get("campus", "both")
    group_size = data.get("group_size", 1)

    if intent == "unknown":
        return jsonify({
            "success": False,
            "message": "Sorry, I couldn't understand your request.",
            "intent": intent
        })

    result = recommend_location(intent, campus, group_size)
    result["intent"] = intent

    return jsonify(result)


@app.route("/api/population", methods=["GET"])
def population_status():
    return jsonify(get_population())


@app.route("/api/occupancy", methods=["POST"])
def change_occupancy():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid data."
        }), 400

    success, message = update_occupancy(
        data.get("library_id"),
        data.get("category"),
        data.get("location_id"),
        data.get("occupied")
    )

    return jsonify({
        "success": success,
        "message": message
    })


@app.route("/api/printer", methods=["POST"])
def change_printer():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid data."
        }), 400

    success, message = update_printer_status(
        data.get("library_id"),
        data.get("status")
    )

    return jsonify({
        "success": success,
        "message": message
    })

@app.route("/api/simulation-settings", methods=["POST"])
def save_simulation_settings():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid settings data."
        }), 400

    success, message = update_all_settings(
        data.get("occupancy"),
        data.get("printers")
    )

    return jsonify({
        "success": success,
        "message": message
    }), 200 if success else 400

if __name__ == "__main__":
    app.run(debug=True)
