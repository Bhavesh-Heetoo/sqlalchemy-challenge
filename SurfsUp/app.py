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
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

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



if __name__ == "__main__":
    app.run(debug=True)
