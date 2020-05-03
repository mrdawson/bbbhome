from flask import render_template, request, jsonify, current_app
from app.spellbook import bp
from flask_login import login_required, current_user
from app.auth.wrappers import roles_required
import os

BBB = os.environ.get("PLATFORM") == "BeagleBone Black"

if BBB:
    from bbbio import AnalogIn
    import board
    import digitalio


@bp.route("/thermostat")
@login_required
@roles_required("Wizard")
def thermostat():
    return render_template("/spellbook/thermostat.html", title="Thermostat")


@bp.route("/thermostat/on_off", methods=["GET", "POST"])
@login_required
@roles_required("Wizard")
def thermostat_on_off():
    if not BBB:
        return "No BeagleBone"
    x = request.form.get('status', 0, type=str)
    led = digitalio.DigitalInOut(board.P9_12)
    led.direction = digitalio.Direction.OUTPUT
    if x == "on":
        led.value = True
        return "Fire ON"
    elif x == "off":
        led.value = False
        return "Fire OFF"


@bp.route('/thermostat/get_status', methods=["GET"])
@login_required
@roles_required("Wizard")
def get_status():
    if not BBB:
        return jsonify([0, 0])

    status = digitalio.DigitalInOut(board.P9_15)
    status.direction = digitalio.Direction.INPUT

    pin = AnalogIn("P9_39")
    temperature = pin.value / 0.02 * 9 / 5 + 32

    return jsonify(["on" if status.value else "off", temperature])
