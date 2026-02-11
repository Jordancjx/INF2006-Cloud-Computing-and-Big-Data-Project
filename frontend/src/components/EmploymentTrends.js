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
  const [viewMode, setViewMode] = useState('trend'); 

  const API_BASE_URL = "http://3.238.41.206:5000";

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
          <h3 className="chart-title">
            {viewMode === 'trend' ? 'Employment Trends Over Time' : `School Breakdown for ${selectedYear}`}
          </h3>
        </div>
        
        <div className="chart-container" style={{ height: '400px' }}>
          {viewMode === 'trend' ? (
            <Line 
                data={{
                    labels: data.trend.map(item => item.year),
                    datasets: [
                        {
                            label: "Overall Rate (%)",
                            data: data.trend.map(item => item.employment_rate_overall),
                            borderColor: "rgb(102, 126, 234)",
                            backgroundColor: "rgba(102, 126, 234, 0.1)",
                            tension: 0.3
                        }
                    ]
                }} 
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (e, el) => el.length > 0 && fetchSchoolBreakdown(data.trend[el[0].index].year)
                }}
            />
          ) : (
            <Bar 
              data={{
                labels: schoolBreakdown?.schools.map(s => s.school),
                datasets: [{
                    label: "Overall Employment (%)",
                    data: schoolBreakdown?.schools.map(s => s.employment_rate_overall),
                    backgroundColor: "rgba(102, 126, 234, 0.7)"
                }]
              }}
              options={{ indexAxis: 'y', responsive: true, maintainAspectRatio: false }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default EmploymentTrends;