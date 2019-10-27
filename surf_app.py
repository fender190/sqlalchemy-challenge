  
# import all necessary dependencies
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# creating and reflecting the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect = True)

# load up tables and create session
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# create Flask app
app = Flask(__name__)

# get dates from query
mx_dt = (session.query(Measurement.date)).\
        order_by(Measurement.date.desc()).first()
mx_dt = list(np.ravel(mx_dt))[0]

max_dt = dt.datetime.strptime(mx_dt,"%Y-%M-%d")
max_dt = max_dt.timetuple()

# get exact time(year or month or day)
year_dt = max_dt[0]-1
month_dt = max_dt[1]
day_dt = max_dt[2]

# last year's date
last_year_dt = dt.date(year_dt,month_dt,day_dt) - dt.timedelta(days=365)

# trip dates (used same dates on python notebook)
start_date_trip = dt.date(2016,10,10)
end_date_trip = dt.date(2016,10,20)

#date temps
def cal_temps(start_date_trip,end_date_trip):
    return session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date_trip).\
            filter(Measurement.date >= end_date_trip).all()

# routes for flask app

@app.route("/")
def Surfs_Up():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
# precipitation
@app.route("/api/v1.0/precipitaton")
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    results=list(np.ravel(results))
    return jsonify(results)

#tobs
@app.route("/api/v1.0/temperature")
def tobs():
   session = Session(engine)
   tobs_results = session.query(Measurement.date, Measurement.tobs).\
       filter(Measurement.date >= last_year_dt).all()
   tobs_list=[]
   for tobs in tobs_results:
       tobs_dict = {}
       tobs_dict[tobs[0]] = float(tobs[1])
       tobs_list.append(tobs_dict)
   return jsonify(tobs_list)

# start trip date
@app.route("/api/v1.0/<start>")
def start(start):
    
    

    #temps using calc_temps
    temps = calc_temps(start, last_year_dt)

    date_list = []
    date_dict = {'start_date': start_date_trip, 'end_date': end_date_trip}
    date_list.append(date_dict)
    date_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    date_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    date_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(date_list)

# end trip date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
   
    #temps using calc_temps
    temps2 = calc_temps(start, end)

    #create a list
    date_end_list = []
    date_dict = {'start_date': start_date_trip, 'end_date': end_date_trip}
    date_end_list.append(date_dict)
    date_end_list.append({'Observation': 'TMIN', 'Temperature': temps2[0][0]})
    date_end_list.append({'Observation': 'TAVG', 'Temperature': temps2[0][1]})
    date_end_list.append({'Observation': 'TMAX', 'Temperature': temps2[0][2]})

    return jsonify(date_end_list)

if __name__ == '__main__':
    app.run(debug=True) 