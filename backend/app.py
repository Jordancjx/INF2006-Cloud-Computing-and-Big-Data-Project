import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
# Import your updated analytics functions
from analytics.employment_trends import employment_trend, employment_by_school
from analytics.salary_correlation import salary_employment_correlation
from analytics.enrollment_analysis import enrollment_graduate_analysis

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_USER = "admin" 
DB_PASSWORD = "adminadmin" 
DB_ENDPOINT = "database-1.cxuyppgplsie.us-east-1.rds.amazonaws.com"
DB_NAME = "ges_data"


DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}:3306/{DB_NAME}"
db_engine = create_engine(DATABASE_URL)

@app.route("/api/analytics/employment-trends")
def get_employment_trends():
    try:
        result = employment_trend(db_engine)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/analytics/employment-by-school")
def get_employment_by_school():
    try:
        year = request.args.get('year', type=int)
        if year is None:
            return jsonify({'success': False, 'error': 'Year parameter is required'}), 400
        
        result = employment_by_school(db_engine, year)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/analytics/salary-employment-correlation")
def get_salary_employment_correlation():
    try:
        year = request.args.get('year', None, type=int)
        school = request.args.get('school', None, type=str)
        result = salary_employment_correlation(db_engine, year, school)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/analytics/enrollment-graduate-analysis")
def get_enrollment_graduate_analysis():
    try:
        start_year = request.args.get('start_year', None, type=int)
        end_year = request.args.get('end_year', None, type=int)
        school_id = request.args.get('school_id', None, type=int)
        
        result = enrollment_graduate_analysis(db_engine, start_year, end_year, school_id)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/health")
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Cloud Backend running on EC2'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)