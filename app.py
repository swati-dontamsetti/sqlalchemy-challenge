# import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start_date<br/>"
        "/api/v1.0/start_date/end_date<br/>"
        "IMPORTANT: Put the start_date and end_date in 'YYYY-MM-DD' format<br/>"
        )


# Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON list of the dates and percipitation from the last year.
    I am adding the station id for clarity."""

    # latest date
    last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date 1 year ago from the last data point in the database
    last_year = dt.datetime.strptime(last[0], '%Y-%m-%d')
    one_year_ago = dt.date(last_year.year -1, last_year.month, last_year.day)

    results = session.query(Measurement.station, Measurement.date, Measurement.prcp)\
                    .filter(Measurement.date >= one_year_ago).all()                                                                  
    
    list = []
    for result in results:
        dict = {"Station":result[0], "Date":result[1], "Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    stations = session.query(Station.station, Station.name).all()
    
    list=[]
    for stat in stations:
        dict = {"Station ID:":stat[0],"Station Name":stat[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # latest date
    last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date 1 year ago from the last data point in the database
    last_year = dt.datetime.strptime(last[0], '%Y-%m-%d')
    one_year_ago = dt.date(last_year.year -1, last_year.month, last_year.day)

    # identify the most active station
    active = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).all()

    tobs = session.query(Measurement.date, Measurement.tobs)\
                            .filter(Measurement.date >= one_year_ago)\
                            .filter(Measurement.station==active[0][0]).all()
    list = []
    for temp in tobs:
        dict = {"Date": temp[0], "Temperature (F)": temp[1]}
        list.append(dict)

    return jsonify(list)  

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of TMIN, TAVG, and TMAX
    for all dates greater than and equal to the start date."""

    results = session.query(func.min(Measurement.tobs),
                     func.max(Measurement.tobs),
                     func.avg(Measurement.tobs))\
             .filter(Measurement.date >= start)\
             .order_by(Measurement.date.desc()).all()

    for result in results:
        dict = {"Min Temp (F)": results[0][0], "Max Temp (F)": results[0][1], "Avg Temp (F)": results[0][2]}

    return jsonify(dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return a JSON list of TMIN, TAVG, and TMAX
    for all dates greater than and equal to the start date."""

    results = session.query(func.min(Measurement.tobs),
                     func.max(Measurement.tobs),
                     func.avg(Measurement.tobs))\
             .filter(Measurement.date >= start, Measurement.date <= end)\
             .order_by(Measurement.date.desc()).all()

    for result in results:
        dict = {"Min Temp (F)": results[0][0], "Max Temp (F)": results[0][1], "Avg Temp (F)": results[0][2]}

    return jsonify(dict)

if __name__ == "__main__":
    app.run(debug=True)
