import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from analytics.employment_trends import employment_trend

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

@app.route("/api/analytics/salary-employment-correlation")
def get_salary_employment_correlation():
    """
    API endpoint for salary vs employment correlation analysis
    Query params: year (optional, default=2023)
    Returns: JSON with correlation data (PLACEHOLDER)
    """
    try:
        year = request.args.get('year', 2023, type=int)
        
        # TODO: Implement backend analytics function
        # from analytics.salary_correlation import salary_employment_correlation
        # result = salary_employment_correlation(GES_CSV_PATH, year)
        
        # Placeholder response
        result = {
            'year': year,
            'data': [
                {'degree': 'Computer Science', 'employment_rate': 95.5, 'median_salary': 5200},
                {'degree': 'Engineering', 'employment_rate': 93.2, 'median_salary': 4800},
                {'degree': 'Business', 'employment_rate': 90.8, 'median_salary': 4200},
                {'degree': 'Accountancy', 'employment_rate': 92.1, 'median_salary': 4100},
                {'degree': 'Information Systems', 'employment_rate': 94.3, 'median_salary': 4900},
                {'degree': 'Sciences', 'employment_rate': 88.5, 'median_salary': 3800},
                {'degree': 'Arts & Social Sciences', 'employment_rate': 85.2, 'median_salary': 3500},
            ],
            'correlation_coefficient': 0.87,
            'message': 'Using placeholder data - Backend analytics not yet implemented'
        }
        
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
        - start_year (optional, default=2018)
        - end_year (optional, default=2023)
    Returns: JSON with enrollment/graduate trends (PLACEHOLDER)
    """
    try:
        start_year = request.args.get('start_year', 2018, type=int)
        end_year = request.args.get('end_year', 2023, type=int)
        
        # TODO: Implement backend analytics function
        # from analytics.enrollment_analysis import enrollment_graduate_analysis
        # result = enrollment_graduate_analysis(
        #     ENROLMENT_CSV_PATH, 
        #     GRADUATES_CSV_PATH,
        #     start_year, 
        #     end_year
        # )
        
        # Placeholder response
        result = {
            'start_year': start_year,
            'end_year': end_year,
            'data': [
                {'year': 2018, 'school_name': 'All Schools', 'enrolment': 45000, 'graduates': 42000, 'completion_rate': 93.3},
                {'year': 2019, 'school_name': 'All Schools', 'enrolment': 46500, 'graduates': 43200, 'completion_rate': 92.9},
                {'year': 2020, 'school_name': 'All Schools', 'enrolment': 47200, 'graduates': 44100, 'completion_rate': 93.4},
                {'year': 2021, 'school_name': 'All Schools', 'enrolment': 48100, 'graduates': 45000, 'completion_rate': 93.6},
                {'year': 2022, 'school_name': 'All Schools', 'enrolment': 49000, 'graduates': 46200, 'completion_rate': 94.3},
                {'year': 2023, 'school_name': 'All Schools', 'enrolment': 50200, 'graduates': 47500, 'completion_rate': 94.6},
            ],
            'average_completion_rate': 93.7,
            'message': 'Using placeholder data - Backend analytics not yet implemented'
        }
        
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
