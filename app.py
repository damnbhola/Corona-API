from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify
import json
from opencage.geocoder import OpenCageGeocode

key = "db5e12475643479390239ad92a1f7698"
geocoder = OpenCageGeocode(key)
app = Flask(__name__)


try:
    page = requests.get("https://bing.com/covid", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362"})
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


@app.route('/location', methods=['GET'])
def get_all_data():
    return jsonify({'data': data})


@app.route('/total', methods=['GET'])
def get_world():
    total = data.copy()
    total["areas"] = []
    return jsonify(total)


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
                                    return jsonify(district_searched)
                        except Exception as e:
                            print(e)
                            return jsonify(state_searched)
            except Exception as e:
                print(e)
                return jsonify(country_searched)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})


@app.route('/location/<string:country>', methods=['GET'])
def get_country(country):
    try:
        country_searched = find_country(country.lower())
        if country_searched:
            return jsonify(country_searched)
    except Exception as e:
        print(e)
    return jsonify({"message": "Not able to Locate."})
