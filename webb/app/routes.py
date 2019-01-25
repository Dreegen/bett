from app import app
from app import get_data
from flask import render_template, flash, redirect
from apscheduler.schedulers.background import BackgroundScheduler

def sensor():
    """ Function for test purposes. """
    global h1_g, h1_s, d1_g, d1_s
    h1_g, h1_s, d1_g, d1_s = get_data.main()
    print("Scheduler is alive!")
    return (h1_g, h1_s, d1_g, d1_s)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor)
sched.add_job(sensor, 'interval', minutes=240)
sched.start()


@app.route('/')
@app.route('/index')
@app.route('/hej')
def index():
    return render_template("analysis.html", h1_g=h1_g, h1_s=h1_s, d1_g=d1_g, d1_s=d1_s)
