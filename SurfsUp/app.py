# Import the dependencies.


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#importing desc function from sqlalchemy
from sqlalchemy import desc
#importing datetime function
import datetime as dt
#importing pandas
import pandas as pd
from flask import Flask, jsonify

#################################################
# Database Setupcan env list

#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table

#saving Station class
Station = Base.classes.station
#saving Measurment class
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """All Available Routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/{{start}}<br/>"
        f"/api/v1.0/{{start}}/{{end}}<br/>"
        f"Note:Please use the date format 'YYYY-MM-DD' for the {{start}} and {{end}} date parameters."
    )
session.close()

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation for last 12 months"""
    # creating a session query to find most recent date
    recent_date_0 = session.query(Measurement.date).order_by(desc(Measurement.date)).first()

    #converting the most recent date to a datetime object
    recent_date = recent_date_0[0]
    recent_date = pd.to_datetime(recent_date)

    #finding the date one year from the last date in data set.
    date_one_year = (recent_date - dt.timedelta(days=365))

    date_one_year_str = date_one_year.strftime('%Y-%m-%d')
    #Creating a query to get data from  last 12 months and putting in ascending order 
    precipitation_date_scores = (session.query(Measurement.date , Measurement.prcp).filter(Measurement.date >= date_one_year_str).order_by(Measurement.date).all())

    #Converting to a dictionary
    precipitation_score_dict = {date: prcp for date, prcp in precipitation_date_scores}
    return jsonify(precipitation_score_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List of stations"""
    # running a query to get stations for stations table
    stations_list = session.query(Station.station).all()
    #converting the tuples into a list
    stations_list_1 = [station[0] for station in stations_list]
    return jsonify(stations_list_1)

@app.route("/api/v1.0/tobs")
def tobs():
    """dates and temperature observations of the most-active station for the previous year of data"""
     # creating a session query to find most recent date
    recent_date_0 = session.query(Measurement.date).order_by(desc(Measurement.date)).first()

    #converting the most recent date to a datetime object
    recent_date = recent_date_0[0]
    recent_date = pd.to_datetime(recent_date)

    #finding the date one year from the last date in data set.
    date_one_year = (recent_date - dt.timedelta(days=365))

    date_one_year_str = date_one_year.strftime('%Y-%m-%d')

    #finding the most active station , joining both tables
    most_active_station = session.query(Station.station,func.count(Station.station)) \
    .join(Measurement, Station.station == Measurement.station)\
    .group_by(Station.station) \
    .order_by(func.count(Station.station).desc()).\
    first()[0]

    #creating the query 
    temps_most_active = session.query(Measurement.date ,Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= date_one_year_str)\
        .all()
    
    #Converting to a dictionary for json 
    tobs_most_active_data = [{"date": date, "temperature": tobs} for date, tobs in temps_most_active ]
     
    return jsonify(tobs_most_active_data)

@app.route("/api/v1.0/<start>")
def start(start):
    """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date"""
    # creating a query based on the specified start date
    start_stats = session.query(func.min(Measurement.tobs) , func.avg(Measurement.tobs) , func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    #creating a dictionary from query and displaying in chart formating 
    start_stats_1 = {
        "Start Date": start ,
        "Min": start_stats[0][0],
        "Avg": start_stats[0][1],
        "Max": start_stats[0][2]
    }
    return jsonify(start_stats_1)
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive"""
     #creating a query based on the specified start date and end date
    start_End_stats = session.query(func.min(Measurement.tobs) , func.avg(Measurement.tobs) , func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <=end).all()
    #creating a dictionary from query and displaying in chart formating 
    start_end_stats_dict = {
        "Start Date": start ,
        "End Date" : end ,
        "Min": start_End_stats[0][0],
        "Avg": start_End_stats[0][1],
        "Max": start_End_stats[0][2]    
    }
    return jsonify(start_end_stats_dict)


if __name__ == "__main__":
    app.run(debug=True)
