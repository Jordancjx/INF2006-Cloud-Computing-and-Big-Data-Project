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
  const [selectedYear, setSelectedYear] = useState(2023);
  const [selectedSchool, setSelectedSchool] = useState("");

  // Initial placeholder data
  const [data, setData] = useState({
    year: 2023,
    available_schools: [],
    selected_school: null,
    data: [
      { degree: "Engineering", employment_rate: 92.5, median_salary: 3800 },
      { degree: "Business", employment_rate: 88.0, median_salary: 3200 },
      { degree: "IT", employment_rate: 94.0, median_salary: 4000 },
      { degree: "Health Sciences", employment_rate: 96.0, median_salary: 3500 },
      { degree: "Arts", employment_rate: 82.0, median_salary: 2800 },
      { degree: "Sciences", employment_rate: 85.0, median_salary: 3000 },
      { degree: "Social Sciences", employment_rate: 84.0, median_salary: 2900 },
    ],
    correlation_coefficient: 0.78,
    message: "Using placeholder data - Backend not yet implemented",
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        let url = `${API_BASE_URL}/api/analytics/salary-employment-correlation?year=${selectedYear}`;
        if (selectedSchool) {
          url += `&school=${encodeURIComponent(selectedSchool)}`;
        }
        
        const response = await fetch(url);
        const result = await response.json();

        if (result.success && result.data.data && result.data.data.length > 0) {
          // Replace placeholder with real data
          setData(result.data);
        } else {
          // Keep placeholder data and show message
          setData((prev) => ({ ...prev, year: selectedYear }));
        }
      } catch (err) {
        console.error("Error fetching salary correlation:", err);
        setError(`Network error: ${err.message}`);
        // Keep placeholder data on error
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [API_BASE_URL, selectedYear, selectedSchool]);

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
      legend: {
        display: true,
        position: "top",
      },
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
        ticks: {
          callback: (value) => `$${value}`,
        },
      },
      y: {
        title: {
          display: true,
          text: "Employment Rate (%)",
          font: { size: 14, weight: "bold" },
        },
        min: 75,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
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
            {[2018, 2019, 2020, 2021, 2022, 2023].map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
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
            {data.available_schools && data.available_schools.map((school) => (
              <option key={school} value={school}>
                {school}
              </option>
            ))}
          </select>
        </div>

        {data.message && <div className="info-message">{data.message}</div>}
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
            {selectedSchool ? `${selectedSchool} - ${data.year}` : `All schools - ${data.year}`}
          </p>
        </div>
      </div>

      <div className="chart-section">
        <h3>Salary vs Employment Rate by Degree</h3>
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
                <td>${item.median_salary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SalaryCorrelation;
