# IMPORT
# flask
from flask import Flask, jsonify, json
# Python 
import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func, or_, and_


# # DATABASE SETUP
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = scoped_session(sessionmaker(bind=engine))

# APP
app = Flask(__name__)

@app.teardown_request
def remove_session(ex=None):
    session.remove()

# ROUTES
# home route
@app.route("/")
def homePage():
    # List all available api routes
    return (
        f'CLIMATE APP<br/>'
        f'<br/>'
        f'AVAILABLE ROUTES:<br/>'
        f'<a href="/api/v1.0/precipitation">precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">stations</a><br/>'
        f'<a href="/api/v1.0/tobs">tobs</a><br/>'
        f'<a href="/api/v1.0/summary_temperature/<start_date>/<end_date>">summary temperature</a>'
    )

# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    queryPrecipitation = session.query(Measurement.prcp, Measurement.date).all()
    dataPrecipitation = []
    for prcp, date in queryPrecipitation:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        dataPrecipitation.append(precipitation_dict)
    return  jsonify(dataPrecipitation)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    dataStations = session.query(Station.station).all()
    dataStations = list(np.ravel(dataStations))
    return jsonify(dataStations)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Last 12 months
    endDate = engine.execute("SELECT max(date) FROM measurement").first()
    endDate = str(endDate).replace(',','').replace('(','').replace(')','').replace("'",'')
    endDate = dt.datetime.strptime(endDate, '%Y-%m-%d')
    startDate = endDate - dt.timedelta(days=365)
    # Query retrieving 12 months
    dataTobs = session.query(Measurement.date, Measurement.tobs)\
        .filter(and_(Measurement.date>=startDate,Measurement.date<=endDate))\
        .order_by(Measurement.date)\
        .all()
    dataTobs = list(np.ravel(dataTobs))
    return jsonify(dataTobs)

# summary_temperature given start or not end date route
@app.route("/api/v1.0/summary_temperature/<start_date>")
@app.route("/api/v1.0/summary_temperature/<start_date>/<end_date>")
def summary_temperature(start_date=None, end_date=None):
    if not end_date:
        summaryTemperature = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
            .filter(Measurement.date>=start_date).all()
        summaryTemperature = list(np.ravel(summaryTemperature))
        return jsonify(summaryTemperature)
    summaryTemperature= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(and_(Measurement.date>=start_date,Measurement.date<=end_date)).all()
    summaryTemperature = list(np.ravel(summaryTemperature))
    return jsonify(summaryTemperature)

# APP RUNNING
if __name__ == "__main__":
    app.run(debug=True)
