from flask import Flask, render_template, jsonify, request
from flaskext.mysql import MySQL
from flask_basicauth import BasicAuth

app = Flask(__name__)


# Uncomment this
#f = open("/var/www/bbbhome/auth.txt", "r")
f = open('auth.txt', 'r')
auth = f.readlines()
auth = [x.strip() for x in auth]
app.config['BASIC_AUTH_USERNAME'] = auth[0]
app.config['BASIC_AUTH_PASSWORD'] = auth[1]

basic_auth = BasicAuth(app)

"""
# Uncomment this
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = auth[2]
app.config['MYSQL_DATABASE_PASSWORD'] = auth[3]
app.config['MYSQL_DATABASE_DB'] = 'bbbhome'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

scheduler = BackgroundScheduler()

# Initialize GPIO pin
GPIO.setup("P9_11", GPIO.OUT, delay=200)
GPIO.setup("P9_11", GPIO.OUT, delay=200)
GPIO.setup("P9_13", GPIO.IN, delay=200)
GPIO.setup("P9_13", GPIO.IN, delay=200)
"""


@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/thermostat')
@basic_auth.required
def thermostat():
    return render_template("thermostat.html")


@app.route('/resume')
def resume():
    return render_template("resume.html")


@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/mac1700')
def mac1700():
    return render_template("mac1700.html")

@app.route('/klh20')
def klh20():
    return render_template("klh20.html")


@app.route('/on_off', methods=['GET', 'POST'])
def on_off():
    x = request.form.get('status', 0, type=int)
    print x
    if x == 1:
        GPIO.output("P9_11", GPIO.HIGH)
        return "Fire ON"
    elif x == 0:
        GPIO.output("P9_11", GPIO.LOW)
        return "Fire OFF"


@app.route('/get_status')
def get_status():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tLog "
                   "WHERE date_time = "
                   "(SELECT MAX(date_time) FROM tLog)")
    temp = cursor.fetchone()
    cursor.close()
    return jsonify([GPIO.input("P9_13"), temp[1]])


def medfilt(x, k):
    assert k % 2 == 1, "Median filter length must be odd."
    # assert x.ndim == 1, "Input must be one-dimenstional."
    k2 = (k-1)//2
    y = np.zeros((len(x), k))
    for i in range(k2):
        j = k2 - i
        y[j:, i] = x[:-j]
        y[:j, i] = x[0]
        y[:-j, -(i+1)] = x[j:]
        y[-j:, -(i+1)] = x[-1]
    return np.median(y, axis=1)


@app.route('/get_t_data')
def get_t_data():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT UNIX_TIMESTAMP(date_time), temperature FROM tLog "
                   "ORDER BY date_time DESC LIMIT 10080")
    data = cursor.fetchall()
    cursor.close()
    times = [0]*len(data)
    temps = [0]*len(data)
    output = [0]*len(data)
    for ii in range(0, len(data)):
        times[ii], temps[ii] = data[ii]
        times[ii] *= 1000
    temps = medfilt(temps, 13)
    for ii in range(0, len(data)):
        output[ii] = [times[ii], temps[ii]]
    return jsonify(output)


if __name__ == '__main__':
    app.run()
