import os
from flask import Flask, jsonify
from flask_cors import CORS
from analytics.employment_trends import employment_trend

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(BASE_DIR, "data", "GES.csv")

@app.route("/analytics/employment-trends")
def get_employment_trends():
    return jsonify(employment_trend(CSV_PATH))

if __name__ == "__main__":
    app.run(debug=True)
