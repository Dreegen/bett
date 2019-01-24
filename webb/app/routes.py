from flask import render_template, flash, redirect
from app import app
from app import get_data
from keras.models import load_model
import numpy as np
import os
import tensorflow as tf
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

# loads and returns a compiled model
global model, graph
model = load_model('v2.h5')
graph = tf.get_default_graph()


def sensor():
    """ Function for test purposes. """
    global x, y
    x, y = get_data.main(
        "https://www.betexplorer.com/handball/sweden/handbollsligan/")
    print("Scheduler is alive!")
    return (x, y)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor)
sched.add_job(sensor, 'interval', minutes=1)
sched.start()


@app.route('/')
@app.route('/index')
def index():
    return render_template("analysis.html", standings=x, next_games=y)


@app.route('/predict')
def predict():
    odds_1 = 0
    odds_x = 1
    odds_2 = 2

    # Make to np.array
    x = np.array([odds_1, odds_x, odds_2])

    # Add the input to a batch where it's the only member.
    x = (np.expand_dims(x, 0))

    with graph.as_default():
        predicted = np.array(model.predict(x))

    prob_1 = predicted[0][0]
    prob_x = predicted[0][1]
    prob_2 = predicted[0][2]

    return render_template("predict.html", predicted=predicted, prob_1=prob_1, prob_x=prob_x, prob_2=prob_2, odds_1=odds_1, odds_x=odds_x, odds_2=odds_2)
