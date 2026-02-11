import React, { useState, useEffect } from "react";
import { Scatter } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import "./SalaryCorrelation.css";

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

const SalaryCorrelation = () => {
  const [selectedYear, setSelectedYear] = useState(2022);
  const [selectedSchool, setSelectedSchool] = useState("");
  
  // Placeholder data removed - initialized as null
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = "http://3.238.41.206:5000";

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        let url = `${API_BASE_URL}/api/analytics/salary-employment-correlation?year=${selectedYear}`;
        if (selectedSchool) {
          url += `&school=${encodeURIComponent(selectedSchool)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();

        if (result.success && result.data) {
          setData(result.data);
        } else {
          setError(result.error || "No data found for the selected criteria");
        }
      } catch (err) {
        console.error("Error fetching salary correlation:", err);
        setError(`Network error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [API_BASE_URL, selectedYear, selectedSchool]);

  // Loading View
  if (loading) {
    return (
      <div className="salary-correlation">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading salary correlation analytics...</p>
        </div>
      </div>
    );
  }

  // Error View
  if (error) {
    return (
      <div className="salary-correlation">
        <div className="error-container">
          <h3>Error Loading Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  // Safety check - if loading is finished but data is still null
  if (!data || !data.data) {
    return (
      <div className="salary-correlation">
        <div className="no-data-container">
          <p>No analytics data available for this selection.</p>
        </div>
      </div>
    );
  }

  // Prepare scatter plot data
  const scatterData = {
    datasets: [
      {
        label: "Degree Programs",
        data: data.data.map((item) => ({
          x: item.median_salary,
          y: item.employment_rate,
          label: item.degree,
        })),
        backgroundColor: "rgba(102, 126, 234, 0.6)",
        borderColor: "rgba(102, 126, 234, 1)",
        pointRadius: 8,
        pointHoverRadius: 10,
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: "top" },
      tooltip: {
        callbacks: {
          label: function (context) {
            const point = context.raw;
            return [
              `Degree: ${point.label}`,
              `Salary: $${context.parsed.x}`,
              `Employment: ${context.parsed.y}%`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Median Monthly Salary ($)",
          font: { size: 14, weight: "bold" },
        },
        ticks: { callback: (value) => `$${value}` },
      },
      y: {
        title: {
          display: true,
          text: "Employment Rate (%)",
          font: { size: 14, weight: "bold" },
        },
        // Dynamically adjust scale based on data if available, or defaults
        ticks: { callback: (value) => `${value}%` },
      },
    },
  };

  return (
    <div className="salary-correlation">
      <h2>Salary vs Employment Correlation</h2>

      <div className="controls-section">
        <div className="year-selector">
          <label>Select Year: </label>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
          >
            {[2018, 2019, 2020, 2021, 2022].map((year) => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        <div className="school-selector">
          <label>Select School: </label>
          <select
            value={selectedSchool}
            onChange={(e) => setSelectedSchool(e.target.value)}
          >
            <option value="">All Schools</option>
            {data.available_schools?.map((school) => (
              <option key={school} value={school}>{school}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="kpi-row">
        <div className="kpi-card">
          <h3>Correlation Coefficient</h3>
          <p className="kpi-value">
            {data.correlation_coefficient !== null
              ? data.correlation_coefficient.toFixed(2)
              : "N/A"}
          </p>
          <p className="kpi-description">
            {data.correlation_coefficient > 0.7
              ? "Strong Positive"
              : data.correlation_coefficient > 0.4
                ? "Moderate Positive"
                : "Weak"}
          </p>
        </div>

        <div className="kpi-card">
          <h3>Programs Analyzed</h3>
          <p className="kpi-value">{data.data.length}</p>
          <p className="kpi-description">
            {selectedSchool ? `${selectedSchool}` : "All schools"} — {data.year}
          </p>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-container">
          <Scatter data={scatterData} options={scatterOptions} />
        </div>
      </div>

      <div className="data-table">
        <h3>Detailed Breakdown</h3>
        <table>
          <thead>
            <tr>
              <th>Degree Program</th>
              <th>Employment Rate</th>
              <th>Median Salary</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((item, index) => (
              <tr key={index}>
                <td>{item.degree}</td>
                <td>{item.employment_rate.toFixed(1)}%</td>
                <td>${item.median_salary.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SalaryCorrelation;