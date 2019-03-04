from app import app
from app import get_data
from flask import render_template, flash, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

def sensor():
    """ Function for test purposes. """
    global h1, d1, h2, d2
    h1, d1, h2, d2 = get_data.main()
    print("Scheduler is alive!")
    return (h1, d1, h2, d2)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor)
sched.add_job(sensor, 'interval', minutes=240)
sched.start()


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", h1=h1, d1=d1, h2=h2, d2=d2)


# @app.route('/dataset')
# def dataset():
#     dataset = pd.read_csv('app/static/download/final_dataset.csv')
#     return render_template("dataset.html", dataset=dataset)
