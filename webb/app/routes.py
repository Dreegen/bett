from app import app
from app import get_data
from flask import render_template, flash, redirect
from apscheduler.schedulers.background import BackgroundScheduler

def sensor():
    """ Function for test purposes. """
    url = "https://www.betexplorer.com/handball/sweden/she-women/"
    global cpl_next_games, cpl_standings
    cpl_next_games, cpl_standings = get_data.main(url)
    print("Scheduler is alive!")
    return (cpl_next_games, cpl_standings)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor)
sched.add_job(sensor, 'interval', minutes=240)
sched.start()


@app.route('/')
@app.route('/index')
@app.route('/hej')
def index():
    return render_template("analysis.html", standings=cpl_standings, next_games=cpl_next_games)
