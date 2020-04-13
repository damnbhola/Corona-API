from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify
import json
from opencage.geocoder import OpenCageGeocode

key = "db5e12475643479390239ad92a1f7698"
geocoder = OpenCageGeocode(key)
app = Flask(__name__)


try:
    page = requests.get("https://bing.com/covid")
    soup = BeautifulSoup(page.content, "html.parser")
    data = soup.find("div").text[9:-1]
    data = json.loads(data)
except Exception as e:
    print(e)
    data = {}


def find_country(cou):
    try:
        for loc in data["areas"]:
            if loc["id"] == cou:
                return loc
    except Exception as e:
        print(e)
    return None


@app.route('/raw', methods=['GET'])
def get_all_data():
    return jsonify(data)


@app.route('/', methods=['GET'])
def get_world():
    temp = {"id": data["displayName"], "totalConfirmed": data["totalConfirmed"],
            "totalDeaths": data["totalDeaths"], "totalRecovered": data["totalRecovered"]}
    return jsonify(temp)


@app.route('/country', methods=['GET'])
def get_all_country():
    temp = []
    for i in data["areas"]:
        temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"], "totalDeaths": i["totalDeaths"],
                     "totalRecovered": i["totalRecovered"], "lat": i["lat"], "long": i["long"]})
    return jsonify(temp)


@app.route('/state', methods=['GET'])
def get_all_state():
    temp = []
    for i in data["areas"]:
        temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"], "totalDeaths": i["totalDeaths"],
                     "totalRecovered": i["totalRecovered"], "lat": i["lat"], "long": i["long"]})
        try:
            for j in i["areas"]:
                temp.append({"id": j["displayName"], "totalConfirmed": j["totalConfirmed"], "totalDeaths": j["totalDeaths"],
                             "totalRecovered": j["totalRecovered"], "lat": j["lat"], "long": j["long"]})
        except Exception as e:
            print(e)
    return jsonify(temp)


@app.route('/location/<float:lat>/<float:long>', methods=['GET'])
def get_data(lat, long):
    try:
        results = geocoder.reverse_geocode(lat, long)
        country = results[0]["components"]["country"]
        country_searched = find_country(country.lower())
        if country_searched:
            try:
                state = results[0]["components"]["state"]
                for state_searched in country_searched["areas"]:
                    if state_searched["displayName"] == state:
                        try:
                            state_district = results[0]["components"]["state_district"]
                            for district_searched in state_searched["areas"]:
                                if district_searched["displayName"] == state_district:
                                    temp = {"id": district_searched["displayName"],
                                            "totalConfirmed":  district_searched["totalConfirmed"],
                                            "totalDeaths": district_searched["totalDeaths"],
                                            "totalRecovered": district_searched["totalRecovered"],
                                            "lat": district_searched["lat"], "long": district_searched["long"]}
                                    return jsonify(temp)
                        except Exception as e:
                            print(e)
                            temp = [{"id": state_searched["displayName"],
                                     "totalConfirmed":  state_searched["totalConfirmed"],
                                     "totalDeaths": state_searched["totalDeaths"],
                                     "totalRecovered": state_searched["totalRecovered"],
                                     "lat": state_searched["lat"], "long": state_searched["long"]}]
                            for i in state_searched["areas"]:
                                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                             "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                             "lat": i["lat"], "long": i["long"]})
                            return jsonify(temp)
            except Exception as e:
                print(e)
                temp = [{"id": country_searched["displayName"], "totalConfirmed": country_searched["totalConfirmed"],
                         "totalDeaths": country_searched["totalDeaths"],
                         "totalRecovered": country_searched["totalRecovered"], "lat": country_searched["lat"],
                         "long": country_searched["long"]}]
                for i in country_searched["areas"]:
                    temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                 "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                 "lat": i["lat"], "long": i["long"]})
                else:
                    try:
                        for j in country_searched["areas"]:
                            for i in j["areas"]:
                                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                             "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                             "lat": i["lat"], "long": i["long"]})
                    except Exception as e:
                        print(e)
                return jsonify(temp)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})


@app.route('/location/<string:country>', methods=['GET'])
def get_country(country):
    try:
        country = country.replace("_", " ")
        country_searched = find_country(country.lower())
        if country_searched:
            temp = [{"id": country_searched["displayName"], "totalConfirmed": country_searched["totalConfirmed"],
                     "totalDeaths": country_searched["totalDeaths"],
                     "totalRecovered": country_searched["totalRecovered"], "lat": country_searched["lat"],
                     "long": country_searched["long"]}]
            for i in country_searched["areas"]:
                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"], "totalDeaths": i["totalDeaths"],
                             "totalRecovered": i["totalRecovered"], "lat": i["lat"], "long": i["long"]})
            else:
                try:
                    for j in country_searched["areas"]:
                        for i in j["areas"]:
                            temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                         "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                         "lat": i["lat"], "long": i["long"]})
                except Exception as e:
                    print(e)
            return jsonify(temp)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})


@app.route('/location/<string:country>/<string:state>', methods=['GET'])
def get_state(country, state):
    try:
        country = country.replace("_", " ")
        country_searched = find_country(country.lower())
        if country_searched:
            try:
                state = state.replace("_", " ")
                for state_searched in country_searched["areas"]:
                    if state_searched["displayName"] == state:
                        temp = [{"id": state_searched["displayName"],
                                 "totalConfirmed": state_searched["totalConfirmed"],
                                 "totalDeaths": state_searched["totalDeaths"],
                                 "totalRecovered": state_searched["totalRecovered"],
                                 "lat": state_searched["lat"], "long": state_searched["long"]}]
                        for i in state_searched["areas"]:
                            temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                         "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                         "lat": i["lat"], "long": i["long"]})
                        return jsonify(temp)
            except Exception as e:
                print(e)
                temp = [{"id": country_searched["displayName"], "totalConfirmed": country_searched["totalConfirmed"],
                         "totalDeaths": country_searched["totalDeaths"],
                         "totalRecovered": country_searched["totalRecovered"], "lat": country_searched["lat"],
                         "long": country_searched["long"]}]
                for i in country_searched["areas"]:
                    temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                 "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                 "lat": i["lat"], "long": i["long"]})
                else:
                    try:
                        for j in country_searched["areas"]:
                            for i in j["areas"]:
                                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                             "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                             "lat": i["lat"], "long": i["long"]})
                    except Exception as e:
                        print(e)
                return jsonify(temp)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})


@app.route('/location/<string:country>/<string:state>/<string:state_district>', methods=['GET'])
def get_district(country, state, state_district):
    try:
        country = country.replace("_", " ")
        country_searched = find_country(country.lower())
        if country_searched:
            try:
                state = state.replace("_", " ")
                for state_searched in country_searched["areas"]:
                    if state_searched["displayName"] == state:
                        try:
                            state_district = state_district.replace("_", " ")
                            for district_searched in state_searched["areas"]:
                                if district_searched["displayName"] == state_district:
                                    temp = {"id": district_searched["displayName"],
                                            "totalConfirmed":  district_searched["totalConfirmed"],
                                            "totalDeaths": district_searched["totalDeaths"],
                                            "totalRecovered": district_searched["totalRecovered"],
                                            "lat": district_searched["lat"], "long": district_searched["long"]}
                                    return jsonify(temp)
                        except Exception as e:
                            print(e)
                            temp = [{"id": state_searched["displayName"],
                                     "totalConfirmed":  state_searched["totalConfirmed"],
                                     "totalDeaths": state_searched["totalDeaths"],
                                     "totalRecovered": state_searched["totalRecovered"],
                                     "lat": state_searched["lat"], "long": state_searched["long"]}]
                            for i in state_searched["areas"]:
                                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                             "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                             "lat": i["lat"], "long": i["long"]})
                            return jsonify(temp)
            except Exception as e:
                print(e)
                temp = [{"id": country_searched["displayName"], "totalConfirmed": country_searched["totalConfirmed"],
                         "totalDeaths": country_searched["totalDeaths"],
                         "totalRecovered": country_searched["totalRecovered"], "lat": country_searched["lat"],
                         "long": country_searched["long"]}]
                for i in country_searched["areas"]:
                    temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                 "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                 "lat": i["lat"], "long": i["long"]})
                else:
                    try:
                        for j in country_searched["areas"]:
                            for i in j["areas"]:
                                temp.append({"id": i["displayName"], "totalConfirmed": i["totalConfirmed"],
                                             "totalDeaths": i["totalDeaths"], "totalRecovered": i["totalRecovered"],
                                             "lat": i["lat"], "long": i["long"]})
                    except Exception as e:
                        print(e)
                return jsonify(temp)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})
