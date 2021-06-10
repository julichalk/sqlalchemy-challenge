
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
app = Flask(__name__)

@app.route("/")
def home():
    print("Server requested climate app home page...")
    return (
        f"Welcome to the Hawaii Climate App!<br/>"
        f"----------------------------------<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br>"
        f"Note: Replace 'start_date' and 'end_date' with your query dates. Format for querying is 'YYYY-MM-DD'"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server requested climate app precipitation page...")

    session = Session(engine)

  
    prcp_data = session.query(measurement.date, measurement.prcp).all()

    session.close()

    prcp_dict = {} 
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    print("Server requested climate app station data...")

 
    session = Session(engine)
    

    results = session.query(station.id, station.station, station.name).all()

    session.close()

   
    list_stations = []

    for st in results:
        station_dict = {}

        station_dict["id"] = st[0]
        station_dict["station"] = st[1]
        station_dict["name"] = st[2]

        list_stations.append(station_dict)

 
    return jsonify(list_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server reuested climate app temp observation data ...")

    
    session = Session(engine)

    

  
    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
                                        order_by(func.count(measurement.station).desc()).\
                                        group_by(measurement.station).\
                                        first()[0]

    
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    format_str = '%Y-%m-%d'
    last_dt = dt.datetime.strptime(last_date, format_str)
    date_oneyearago = last_dt - dt.timedelta(days=365)

 
    most_active_tobs = session.query(measurement.date, measurement.tobs).\
                                    filter((measurement.station == most_active_station)\
                                            & (measurement.date >= date_oneyearago)\
                                            & (measurement.date <= last_dt)).all()

  
    session.close()

    
    return jsonify(most_active_tobs)

@app.route("/api/v1.0/<start>")
def temps_from_start(start):
   

    print(f"Server requested climate app daily normals from {start}...")

    
    def daily_normals(start_date):

        
        session = Session(engine)   

        sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= func.strftime("%Y-%m-%d", start_date)).group_by(measurement.date).all()

        
        session.close()

    try:
       
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        results = daily_normals(start_date)
        normals=[]

        for temp_date, tmin, tavg, tmax in results:

           
            temps_dict = {}
            temps_dict["Date"] = temp_date
            temps_dict["T-Min"] = tmin
            temps_dict["T-Avg"] = tavg
            temps_dict["T-Max"] = tmax

           
            normals.append(temps_dict)

        
        return jsonify(normals)

    except ValueError:
        return "Please enter a start date in the format 'YYYY-MM-DD'"
    

@app.route("/api/v1.0/<start>/<end>")
def temps_between(start, end):


    print(f"Server requested climate app daily normals from {start} to {end}...")

    
    def daily_normals(start_date, end_date):

        
        session = Session(engine)   

        sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= func.strftime("%Y-%m-%d", start_date)).\
                                   filter(func.strftime("%Y-%m-%d", measurement.date) <= func.strftime("%Y-%m-%d", end_date)).\
                                    group_by(measurement.date).all()

        
        session.close()

    try:
        
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
        
        results = daily_normals(start_date, end_date)
        normals=[]
        for temp_date, tmin, tavg, tmax in results:

        
            temps_dict = {}
            temps_dict["Date"] = temp_date
            temps_dict["T-Min"] = tmin
            temps_dict["T-Avg"] = tavg
            temps_dict["T-Max"] = tmax

            normals.append(temps_dict)

        
        return jsonify(normals)

    except ValueError:
        return "Please enter dates in the following order and format: 'start_date/end_date' i.e. 'YYYY-MM-DD'/'YYYY-MM-DD'"

if __name__ == "__main__":
    app.run(debug=True)