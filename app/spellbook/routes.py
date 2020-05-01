from flask import render_template, request, jsonify, current_app
from app.spellbook import bp
from flask_login import login_required, current_user
from app.auth.wrappers import roles_required


@bp.record
def setup(state):
    if state.app.config['PLATFORM'] == "BeagleBone Black":
        print('here')
        import adafruit_blinka.agnostic
        import board
        import digitalio
        import analogio


@bp.route("/thermostat")
@login_required
@roles_required("Wizard")
def thermostat():
    return render_template("/spellbook/thermostat.html", title="Thermostat")



@bp.route("/thermostat/on_off", methods=["GET", "POST"])
@login_required
@roles_required("Wizard")
def thermostat_on_off():
    x = request.form.get('status', 0, type=int)
    print(x)
    if x == 1:
        return "Fire ON"
    elif x == 0:
        return "Fire OFF"


@bp.route('/thermostat/get_status')
@login_required
@roles_required("Wizard")
def get_status():
    temp = 68.1
    return jsonify([1, temp])