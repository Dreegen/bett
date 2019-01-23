import tensorflow as tf
from flask import Flask, flash, redirect, render_template, request, session
from keras.models import load_model
import numpy as np
import os

# initalize flask app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# loads and returns a compiled model
global model, graph
model = load_model('v2.h5')
graph = tf.get_default_graph()


@app.route('/')
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        # FEATURES (odds) for the match
        odds_1 = request.form.get("odds_1")
        odds_x = request.form.get("odds_x")
        odds_2 = request.form.get("odds_2")

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

    if request.method == "GET":
        return render_template("index.html")


if __name__ == "__main__":
    # decide what port to run the app in
    port = int(os.environ.get('PORT', 5000))
    # run the app locally on the givn port
    app.run(host='0.0.0.0', port=port)
    # optional if we want to run in debugging mode
    # app.run(debug=True)
