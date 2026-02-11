import React, { useState, useEffect } from "react";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "./EmploymentTrends.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const EmploymentTrends = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [schoolBreakdown, setSchoolBreakdown] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [viewMode, setViewMode] = useState('trend'); // 'trend', 'breakdown', or 'degree'
  const [degreeBreakdown, setDegreeBreakdown] = useState(null);
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('overall'); // 'overall' or 'ft_perm'

  const API_BASE_URL = "";

  const fetchSchoolBreakdown = async (year) => {
    setLoadingBreakdown(true);
    setViewMode('breakdown');
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/employment-by-school?year=${year}`);
      const result = await response.json();
      if (result.success) {
        setSchoolBreakdown(result.data);
        setSelectedYear(year);
      }
    } catch (err) {
      console.error("Error fetching school breakdown:", err);
      setViewMode('trend');
    } finally {
      setLoadingBreakdown(false);
    }
  };

  // Fetch degree breakdown when a school bar is clicked
  const fetchDegreeBreakdown = async (schoolName, metricType) => {
    setLoadingBreakdown(true);
    setViewMode('degree');
    setSelectedMetric(metricType);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/analytics/employment-by-degree?year=${selectedYear}&school=${encodeURIComponent(schoolName)}&metric_type=${metricType}`
      );
      const result = await response.json();
      
      if (result.success) {
        // Check if we have any degree data
        if (result.data.degrees && result.data.degrees.length > 0) {
          setDegreeBreakdown(result.data);
          setSelectedSchool(schoolName);
        } else {
          // No degree data available, show alert and stay in breakdown view
          alert(`No degree data available for ${schoolName} in ${selectedYear}`);
          setViewMode('breakdown');
        }
      } else {
        // API returned an error
        console.error("API error:", result.error);
        setViewMode('breakdown');
      }
    } catch (err) {
      console.error("Error fetching degree breakdown:", err);
      setViewMode('breakdown');
    } finally {
      setLoadingBreakdown(false);
    }
  };

  // Go back to school breakdown view
  const backToSchools = () => {
    setViewMode('breakdown');
    setDegreeBreakdown(null);
    setSelectedSchool(null);
  };

  // Go back to trend view
  const backToTrend = () => {
    setViewMode('trend');
    setSchoolBreakdown(null);
    setDegreeBreakdown(null);
    setSelectedYear(null);
    setSelectedSchool(null);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/employment-trends`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const result = await response.json();
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.error || "Failed to fetch data");
        }
      } catch (err) {
        setError(`Network error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [API_BASE_URL]);

  if (loading) {
    return (
      <div className="enrollment-analysis">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading employment trends analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="enrollment-analysis">
        <div className="error-container">
          <h3>Error Loading Data</h3>
          <p>{error}</p>
          <button className="retry-btn" onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  if (!data || !data.trend) return null;

  const { kpis } = data;

  // Prepare chart data for Line chart
  const chartData = {
    labels: data.trend.map(item => item.year),
    datasets: [
      {
        label: "Overall Employment Rate (%)",
        data: data.trend.map(item => item.employment_rate_overall),
        borderColor: "rgb(102, 126, 234)",
        backgroundColor: "rgba(102, 126, 234, 0.1)",
        tension: 0.3,
        fill: true
      },
      {
        label: "Full-Time Permanent Rate (%)",
        data: data.trend.map(item => item.employment_rate_ft_perm),
        borderColor: "rgb(118, 75, 162)",
        backgroundColor: "rgba(118, 75, 162, 0.1)",
        tension: 0.3,
        fill: true
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        const year = data.trend[index].year;
        fetchSchoolBreakdown(year);
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: { size: 14 },
          padding: 15
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`
        },
        title: {
          display: true,
          text: 'Employment Rate (%)',
          font: { size: 14, weight: 'bold' }
        }
      },
      x: {
        title: {
          display: true,
          text: 'Year',
          font: { size: 14, weight: 'bold' }
        }
      }
    }
  };

  return (
    <div className="enrollment-analysis">
      <h2 className="section-title">Employment Rate Analytics</h2>

      {/* KPI Cards section matching Salary/Enrollment */}
      <div className="kpi-cards">
        <div className="kpi-card">
          <div className="kpi-icon">📈</div>
          <h3>Avg Overall Employment</h3>
          <p className="kpi-value">{kpis.avg_employment_rate_overall?.toFixed(1)}%</p>
          <p className="kpi-description">2013-2023 Average</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">💼</div>
          <h3>Avg FT Permanent</h3>
          <p className="kpi-value">{kpis.avg_employment_rate_ft_perm?.toFixed(1)}%</p>
          <p className="kpi-description">Full-time stability</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">⚖️</div>
          <h3>Stability Ratio</h3>
          <p className="kpi-value">{(kpis.stability_ratio * 100).toFixed(1)}%</p>
          <p className="kpi-description">FT Perm / Overall</p>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-header">
          {viewMode === 'breakdown' && (
            <button className="back-btn" onClick={() => setViewMode('trend')}>← Back to Trends</button>
          )}
          {viewMode === 'degree' && (
            <button className="back-btn" onClick={backToSchools}>
              ← Back to Schools
            </button>
          )}
          <h3 className="chart-title">
            {viewMode === 'trend' 
              ? 'Employment Rate Trends Over Time' 
              : viewMode === 'breakdown'
              ? `School Breakdown for ${selectedYear}`
              : `${selectedMetric === 'overall' ? 'Overall' : 'Full-Time Permanent'} Employment Rate by Degree - ${selectedSchool} (${selectedYear})`}
          </h3>
        </div>
        
        {viewMode === 'trend' && (
          <p className="chart-hint">💡 Click on any year to see school breakdown</p>
        )}
        {viewMode === 'breakdown' && (
          <p className="chart-hint">💡 Click on any bar to see degree breakdown</p>
        )}
        
        <div className="chart-container">
          {loadingBreakdown ? (
            <div className="loading-breakdown">
              <div className="spinner"></div>
              <p>Loading {viewMode === 'breakdown' ? 'school' : 'degree'} data...</p>
            </div>
          ) : viewMode === 'trend' ? (
            <Line data={chartData} options={chartOptions} />
          ) : viewMode === 'breakdown' && schoolBreakdown ? (
            <Bar 
              data={{
                labels: schoolBreakdown.schools.map(s => s.school),
                datasets: [
                  {
                    label: "Overall Employment Rate (%)",
                    data: schoolBreakdown.schools.map(s => s.employment_rate_overall),
                    backgroundColor: "rgba(102, 126, 234, 0.7)",
                    borderColor: "rgb(102, 126, 234)",
                    borderWidth: 2,
                  },
                  {
                    label: "Full-Time Permanent Rate (%)",
                    data: schoolBreakdown.schools.map(s => s.employment_rate_ft_perm),
                    backgroundColor: "rgba(118, 75, 162, 0.7)",
                    borderColor: "rgb(118, 75, 162)",
                    borderWidth: 2,
                  }
                ]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                onClick: (event, elements) => {
                  if (elements.length > 0) {
                    const schoolIndex = elements[0].index;
                    const datasetIndex = elements[0].datasetIndex;
                    const schoolName = schoolBreakdown.schools[schoolIndex].school;
                    const metricType = datasetIndex === 0 ? 'overall' : 'ft_perm';
                    fetchDegreeBreakdown(schoolName, metricType);
                  }
                },
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => `${context.dataset.label}: ${context.parsed.x.toFixed(1)}%`
                    }
                  }
                },
                scales: {
                  x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                      callback: (value) => `${value}%`
                    }
                  }
                }
              }}
            />
          ) : viewMode === 'degree' && degreeBreakdown ? (
            <Bar 
              data={{
                labels: degreeBreakdown.degrees.map(d => d.degree),
                datasets: [
                  {
                    label: `${selectedMetric === 'overall' ? 'Overall' : 'Full-Time Permanent'} Employment Rate (%)`,
                    data: degreeBreakdown.degrees.map(d => d.employment_rate),
                    backgroundColor: selectedMetric === 'overall' 
                      ? "rgba(102, 126, 234, 0.7)" 
                      : "rgba(118, 75, 162, 0.7)",
                    borderColor: selectedMetric === 'overall' 
                      ? "rgb(102, 126, 234)" 
                      : "rgb(118, 75, 162)",
                    borderWidth: 2,
                  }
                ]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => `${context.dataset.label}: ${context.parsed.x.toFixed(1)}%`
                    }
                  }
                },
                scales: {
                  x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                      callback: (value) => `${value}%`
                    }
                  }
                }
              }}
            />
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default EmploymentTrends;