import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import './EmploymentTrends.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const EmploymentTrends = () => {
  // Initial placeholder data
  const [data, setData] = useState({
    trend: [
      { year: 2013, employment_rate_overall: 85.0, employment_rate_ft_perm: 68.0 },
      { year: 2014, employment_rate_overall: 86.0, employment_rate_ft_perm: 69.0 },
      { year: 2015, employment_rate_overall: 87.0, employment_rate_ft_perm: 70.0 },
      { year: 2016, employment_rate_overall: 88.0, employment_rate_ft_perm: 71.0 },
      { year: 2017, employment_rate_overall: 89.0, employment_rate_ft_perm: 72.0 },
      { year: 2018, employment_rate_overall: 89.5, employment_rate_ft_perm: 72.5 },
      { year: 2019, employment_rate_overall: 90.0, employment_rate_ft_perm: 73.0 },
      { year: 2020, employment_rate_overall: 88.0, employment_rate_ft_perm: 71.0 },
      { year: 2021, employment_rate_overall: 89.0, employment_rate_ft_perm: 72.0 },
      { year: 2022, employment_rate_overall: 90.5, employment_rate_ft_perm: 74.0 },
      { year: 2023, employment_rate_overall: 91.0, employment_rate_ft_perm: 75.0 }
    ],
    kpis: {
      avg_employment_rate_overall: 88.5,
      avg_employment_rate_ft_perm: 71.5,
      stability_ratio: 0.82,
      trend_strength: 0.5
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // API base URL - change this when deploying to AWS
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/employment-trends`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();

        if (result.success) {
          // Replace placeholder data with real data from backend
          setData(result.data);
        } else {
          setError(result.error || 'Failed to fetch data');
        }
      } catch (err) {
        console.error('Error fetching employment trends:', err);
        setError(`Network error: ${err.message}`);
        // Keep placeholder data if backend fails
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [API_BASE_URL]);

  if (loading) {
    return (
      <div className="employment-trends">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading employment trends analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="employment-trends">
        <div className="error-container">
          <h3>Error Loading Data</h3>
          <p>{error}</p>
          <p className="error-hint">Make sure the Flask backend is running on port 5000</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  if (!data || !data.trend || data.trend.length === 0) {
    return (
      <div className="employment-trends">
        <div className="no-data-container">
          <p>No data available</p>
        </div>
      </div>
    );
  }

  // Prepare chart data from state (either placeholder or real data)
  const chartData = {
    labels: data.trend.map(item => item.year),
    datasets: [
      {
        label: 'Overall Employment Rate (%)',
        data: data.trend.map(item => item.employment_rate_overall),
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 3
      },
      {
        label: 'Full-Time Permanent Rate (%)',
        data: data.trend.map(item => item.employment_rate_ft_perm),
        borderColor: 'rgb(118, 75, 162)',
        backgroundColor: 'rgba(118, 75, 162, 0.1)',
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 3
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            weight: '500'
          },
          padding: 15,
          usePointStyle: true
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toFixed(1) + '%';
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: value => `${value}%`,
          font: {
            size: 12
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        ticks: {
          font: {
            size: 12
          }
        },
        grid: {
          display: false
        }
      }
    }
  };

  const { kpis } = data;

  const getTrendIcon = (strength) => {
    if (strength === null || strength === undefined) return '—';
    return strength > 0 ? '+' : strength < 0 ? '-' : '=';
  };

  const getTrendClass = (strength) => {
    if (strength === null || strength === undefined) return '';
    return strength > 0 ? 'positive' : strength < 0 ? 'negative' : '';
  };

  return (
    <div className="employment-trends">
      <h2 className="section-title">Employment Rate Analytics</h2>
      
      <div className="kpi-cards">
        <div className="kpi-card">
          <div className="kpi-icon"></div>
          <h3>Avg Overall Employment</h3>
          <p className="kpi-value">
            {kpis.avg_employment_rate_overall 
              ? `${kpis.avg_employment_rate_overall.toFixed(1)}%`
              : 'N/A'}
          </p>
          <p className="kpi-description">Average employment rate across all years</p>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon"></div>
          <h3>Avg FT Permanent</h3>
          <p className="kpi-value">
            {kpis.avg_employment_rate_ft_perm 
              ? `${kpis.avg_employment_rate_ft_perm.toFixed(1)}%`
              : 'N/A'}
          </p>
          <p className="kpi-description">Average full-time permanent employment</p>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon"></div>
          <h3>Stability Ratio</h3>
          <p className="kpi-value">
            {kpis.stability_ratio 
              ? `${(kpis.stability_ratio * 100).toFixed(1)}%`
              : 'N/A'}
          </p>
          <p className="kpi-description">FT Permanent / Overall Employment</p>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">{getTrendIcon(kpis.trend_strength)}</div>
          <h3>Trend Strength</h3>
          <p className={`kpi-value ${getTrendClass(kpis.trend_strength)}`}>
            {kpis.trend_strength !== null && kpis.trend_strength !== undefined
              ? `${kpis.trend_strength > 0 ? '+' : ''}${kpis.trend_strength.toFixed(3)}%`
              : 'N/A'}
          </p>
          <p className="kpi-description">Year-over-year trend change</p>
        </div>
      </div>

      <div className="chart-section">
        <h3 className="chart-title">Employment Rate Trends Over Time</h3>
        <div className="chart-container">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      <div className="insights-section">
        <h3>Key Insights</h3>
        <ul>
          <li>
            <strong>Overall Employment:</strong> Average rate of {kpis.avg_employment_rate_overall?.toFixed(1)}% 
            across all institutions from 2013-2023
          </li>
          <li>
            <strong>Job Stability:</strong> {(kpis.stability_ratio * 100)?.toFixed(0)}% of employed graduates 
            secure full-time permanent positions
          </li>
          <li>
            <strong>Trend:</strong> Employment rates are {kpis.trend_strength >= 0 ? 'increasing' : 'decreasing'} 
            by approximately {Math.abs(kpis.trend_strength)?.toFixed(3)}% per year
          </li>
        </ul>
      </div>
    </div>
  );
};

export default EmploymentTrends;
