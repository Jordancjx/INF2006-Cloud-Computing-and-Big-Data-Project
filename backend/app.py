import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from analytics.employment_trends import employment_trend, employment_by_school
from analytics.salary_correlation import salary_employment_correlation
from analytics.enrollment_analysis import enrollment_graduate_analysis

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GES_CSV_PATH = os.path.join(BASE_DIR, "data", "GES_cleaned.csv")
ENROLMENT_CSV_PATH = os.path.join(BASE_DIR, "data", "Enrolment_cleaned.csv")
GRADUATES_CSV_PATH = os.path.join(BASE_DIR, "data", "Graduates_cleaned.csv")
SCHOOLS_CSV_PATH = os.path.join(BASE_DIR, "data", "schools_lookup.csv")

@app.route("/api/analytics/employment-trends")
def get_employment_trends():
    """
    API endpoint for employment trends analytics
    Returns: JSON with trend data and KPIs
    """
    try:
        result = employment_trend(GES_CSV_PATH)
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/analytics/employment-by-school")
def get_employment_by_school():
    """
    API endpoint for employment breakdown by school for a specific year
    Query params: year (required)
    Returns: JSON with school-level employment data
    """
    try:
        year = request.args.get('year', type=int)
        if year is None:
            return jsonify({
                'success': False,
                'error': 'Year parameter is required'
            }), 400
        
        result = employment_by_school(GES_CSV_PATH, year)
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
    """
    API endpoint for salary vs employment correlation analysis
    Query params: 
        - year (optional, default=latest available year)
        - school (optional, filter by specific school name)
    Returns: JSON with correlation data and statistics
    """
    try:
        year = request.args.get('year', None, type=int)
        school = request.args.get('school', None, type=str)
        result = salary_employment_correlation(GES_CSV_PATH, year, school)
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
    """
    API endpoint for enrollment vs graduates analysis
    Query params: 
        - start_year (optional)
        - end_year (optional)
        - school_id (optional, for filtering by specific school)
    Returns: JSON with enrollment/graduate trends and statistics
    """
    try:
        start_year = request.args.get('start_year', None, type=int)
        end_year = request.args.get('end_year', None, type=int)
        school_id = request.args.get('school_id', None, type=int)
        
        result = enrollment_graduate_analysis(
            ENROLMENT_CSV_PATH, 
            GRADUATES_CSV_PATH,
            start_year, 
            end_year,
            school_id
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
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running',
        'endpoints': {
            'employment_trends': '/api/analytics/employment-trends',
            'salary_correlation': '/api/analytics/salary-employment-correlation',
            'enrollment_analysis': '/api/analytics/enrollment-graduate-analysis'
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
