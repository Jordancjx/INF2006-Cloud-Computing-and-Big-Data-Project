import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
# Import your updated analytics functions
from analytics.employment_trends import employment_trend, employment_by_school, employment_by_degree
from analytics.salary_correlation import salary_employment_correlation, degree_historical_trends
from analytics.enrollment_analysis import enrollment_graduate_analysis, enrollment_by_school_for_year

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

@app.route("/api/analytics/employment-by-degree")
def get_employment_by_degree():
    """
    API endpoint for employment breakdown by degree for a specific school and year
    Query params: year (required), school (required), metric_type (optional, default='overall')
    Returns: JSON with degree-level employment data
    """
    try:
        year = request.args.get('year', type=int)
        school = request.args.get('school', type=str)
        metric_type = request.args.get('metric_type', 'overall', type=str)
        
        if year is None:
            return jsonify({
                'success': False,
                'error': 'Year parameter is required'
            }), 400
        
        if school is None:
            return jsonify({
                'success': False,
                'error': 'School parameter is required'
            }), 400
        
        if metric_type not in ['overall', 'ft_perm']:
            return jsonify({
                'success': False,
                'error': 'metric_type must be "overall" or "ft_perm"'
            }), 400
        
        result = employment_by_degree(GES_CSV_PATH, year, school, metric_type)
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/analytics/salary-employment-correlation")
def get_salary_employment_correlation():
    try:
        year = request.args.get('year', None, type=int)
        school = request.args.get('school', None, type=str)
        result = salary_employment_correlation(db_engine, year, school)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/analytics/degree-historical-trends")
def get_degree_historical_trends():
    """
    API endpoint for degree historical trends (salary and employment over time)
    Query params:
        - degree (required)
        - school (optional, filter by specific school)
    Returns: JSON with year-by-year trends for the degree
    """
    try:
        degree = request.args.get('degree', None, type=str)
        school = request.args.get('school', None, type=str)
        
        if degree is None:
            return jsonify({
                'success': False,
                'error': 'Degree parameter is required'
            }), 400
        
        result = degree_historical_trends(GES_CSV_PATH, degree, school)
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

@app.route("/api/analytics/enrollment-by-school-year")
def get_enrollment_by_school_year():
    """
    API endpoint for enrollment breakdown by school for a specific year
    Query params: 
        - year (required)
    Returns: JSON with school-level enrollment and graduate data for the specified year
    """
    try:
        year = request.args.get('year', None, type=int)
        
        if year is None:
            return jsonify({
                'success': False,
                'error': 'Year parameter is required'
            }), 400
        
        result = enrollment_by_school_for_year(
            ENROLMENT_CSV_PATH,
            GRADUATES_CSV_PATH,
            year
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/health")
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Cloud Backend running on EC2'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)