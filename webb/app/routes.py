from app import app
from app import get_data
from flask import render_template, flash, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

def sensor():
    """ Function for test purposes. """
    global h1_g, h1_s, d1_g, d1_s, h2_g, h2_s, d2_g, d2_s
    h1_g, h1_s, d1_g, d1_s, h2_g, h2_s, d2_g, d2_s = get_data.main()
    print("Scheduler is alive!")
    return (h1_g, h1_s, d1_g, d1_s, h2_g, h2_s, d2_g, d2_s)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor)
sched.add_job(sensor, 'interval', minutes=240)
sched.start()


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", h1_g=h1_g, d1_g=d1_g, h2_g=h2_g, d2_g=d2_g)


# @app.route('/dataset')
# def dataset():
#     dataset = pd.read_csv('app/static/download/final_dataset.csv')
#     return render_template("dataset.html", dataset=dataset)
