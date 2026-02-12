import React, { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "./EnrollmentAnalysis.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const EnrollmentAnalysis = () => {
  const [startYear, setStartYear] = useState(2018);
  const [endYear, setEndYear] = useState(2023);
  const [viewMode, setViewMode] = useState('chart'); // 'chart' or 'breakdown'
  const [selectedYear, setSelectedYear] = useState(null);
  const [schoolBreakdown, setSchoolBreakdown] = useState(null);
  const [insightsExpanded, setInsightsExpanded] = useState(false);

  const [data, setData] = useState({
    start_year: 2018,
    end_year: 2023,
    data: [],
    average_completion_rate: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = "http://INF2006-ALB-1647200621.us-east-1.elb.amazonaws.com"; 

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/analytics/enrollment-graduate-analysis?start_year=${startYear}&end_year=${endYear}`,
        );
        const result = await response.json();

        if (result.success && result.data.data && result.data.data.length > 0) {
          setData(result.data);
        } else {
          setData((prev) => ({
            ...prev,
            start_year: startYear,
            end_year: endYear,
            data: [],
          }));
        }
      } catch (err) {
        console.error("Error fetching enrollment analysis:", err);
        setError(`Network error: ${err.message}`);
        // Keep placeholder data on error
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [API_BASE_URL, startYear, endYear]);

  const fetchSchoolBreakdown = async (year) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/analytics/enrollment-by-school-year?year=${year}`,
      );
      const result = await response.json();

      if (result.success) {
        setSchoolBreakdown(result.data);
        setSelectedYear(year);
        setViewMode('breakdown');
      } else {
        alert(`Failed to load school breakdown: ${result.error}`);
      }
    } catch (err) {
      console.error("Error fetching school breakdown:", err);
      alert(`Network error: ${err.message}`);
    }
  };

  const handleBackToChart = () => {
    setViewMode('chart');
    setSchoolBreakdown(null);
    setSelectedYear(null);
  };

  if (loading) {
    return (
      <div className="enrollment-analysis">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading enrollment analysis...</p>
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
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = {
    labels: data.data.map((item) => item.year),
    datasets: [
      {
        label: "Enrolment",
        data: data.data.map((item) => item.enrolment),
        backgroundColor: "rgba(102, 126, 234, 0.7)",
        borderColor: "rgba(102, 126, 234, 1)",
        borderWidth: 2,
      },
      {
        label: "Graduates",
        data: data.data.map((item) => item.graduates),
        backgroundColor: "rgba(118, 75, 162, 0.7)",
        borderColor: "rgba(118, 75, 162, 1)",
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        const year = data.data[index].year;
        fetchSchoolBreakdown(year);
      }
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: { size: 14 },
          padding: 15,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => value.toLocaleString(),
        },
        title: {
          display: true,
          text: "Number of Students",
          font: { size: 14, weight: "bold" },
        },
      },
      x: {
        title: {
          display: true,
          text: "Year",
          font: { size: 14, weight: "bold" },
        },
      },
    },
  };

  return (
    <div className="enrollment-analysis">
      <h2>Enrollment vs Graduates Analysis</h2>

      {viewMode === 'breakdown' && (
        <button className="back-btn" onClick={handleBackToChart}>
          ← Back to Trends
        </button>
      )}

      {viewMode === 'chart' && (
        <>
          <div className="controls-section">
            <div className="year-range-selector">
              <div className="year-input">
                <label>Start Year: </label>
                <select
                  value={startYear}
                  onChange={(e) => setStartYear(Number(e.target.value))}
                >
                  {[
                    2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022,
                    2023,
                  ].map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>

              <div className="year-input">
                <label>End Year: </label>
                <select
                  value={endYear}
                  onChange={(e) => setEndYear(Number(e.target.value))}
                >
                  {[
                    2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022,
                    2023,
                  ].map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="kpi-row">
            <div className="kpi-card">
              <h3>Average Completion Rate</h3>
              <p className="kpi-value">
                {data.average_completion_rate !== null
                  ? `${data.average_completion_rate.toFixed(1)}%`
                  : "N/A"}
              </p>
              <p className="kpi-description">
                {data.start_year} - {data.end_year}
              </p>
            </div>

            <div className="kpi-card">
              <h3>Total Data Points</h3>
              <p className="kpi-value">{data.data.length}</p>
              <p className="kpi-description">Years analyzed</p>
            </div>

            <div className="kpi-card">
              <h3>Latest Enrolment</h3>
              <p className="kpi-value">
                {data.data.length > 0
                  ? data.data[data.data.length - 1].enrolment.toLocaleString()
                  : "N/A"}
              </p>
              <p className="kpi-description">Year {data.end_year}</p>
            </div>

            <div className="kpi-card">
              <h3>Latest Graduates</h3>
              <p className="kpi-value">
                {data.data.length > 0
                  ? data.data[data.data.length - 1].graduates.toLocaleString()
                  : "N/A"}
              </p>
              <p className="kpi-description">Year {data.end_year}</p>
            </div>
          </div>

          <div className="chart-section">
            <h3>Enrollment vs Graduates Trend</h3>
            <p className="chart-hint">💡 Click on any year to see school breakdown</p>
            <div className="insights-box">
              <h4 onClick={() => setInsightsExpanded(!insightsExpanded)} className="insights-header">
                📊 What This Graph Shows {insightsExpanded ? '▼' : '▶'}
              </h4>
              {insightsExpanded && (
              <>
              <ul>
                <li><strong>Completion Rate Trends:</strong> The gap between bars shows student retention from enrollment to graduation</li>
                <li><strong>Attrition Patterns:</strong> Widening gaps indicate higher dropout rates or program extensions that may need addressing</li>
                <li><strong>Growth Indicators:</strong> Increasing enrollment numbers show program popularity, but check if graduation rates keep pace</li>
                <li><strong>Educational Efficiency:</strong> Years where graduation closely matches enrollment suggest effective student support systems</li>
              </ul>
              <p className="audience-note"><em>For students: Look for consistent graduation numbers | For counsellors: Identify retention challenges | For admins: Track capacity utilization and student success rates</em></p>
              </>
              )}
            </div>
            <div className="chart-container">
              <Bar data={chartData} options={chartOptions} />
            </div>
          </div>

          <div className="data-table">
            <h3>Detailed Breakdown</h3>
            <table>
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Enrolment</th>
                  <th>Graduates</th>
                  <th>Completion Rate</th>
                </tr>
              </thead>
              <tbody>
                {data.data.map((item, index) => (
                  <tr key={index}>
                    <td>{item.year}</td>
                    <td>{item.enrolment.toLocaleString()}</td>
                    <td>{item.graduates.toLocaleString()}</td>
                    <td>{item.completion_rate.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {viewMode === 'breakdown' && schoolBreakdown && (
        <div className="school-breakdown-view">
          <h3>School Breakdown for Year {selectedYear}</h3>
          <p className="breakdown-info">
            Total Schools: {schoolBreakdown.total_schools}
          </p>

          <div className="chart-section">
            <h3>School Comparison (Enrolment vs Graduates)</h3>
            <div className="insights-box">
              <h4 onClick={() => setInsightsExpanded(!insightsExpanded)} className="insights-header">
                📊 What This Graph Shows {insightsExpanded ? '▼' : '▶'}
              </h4>
              {insightsExpanded && (
              <>
              <ul>
                <li><strong>Institutional Scale:</strong> Compare enrollment capacity and graduate output across different institutions</li>
                <li><strong>Completion Rate Comparison:</strong> Identify which schools most effectively graduate their enrolled students</li>
                <li><strong>Outlier Detection:</strong> Schools with unusually low completion rates may indicate systemic support issues or program challenges</li>
                <li><strong>Resource Effectiveness:</strong> Assess if institutions are optimizing their capacity to convert enrollments into graduations</li>
              </ul>
              <p className="audience-note"><em>For students: Choose schools with strong completion records | For counsellors: Understand school-specific challenges | For admins: Benchmark against peer institutions</em></p>
              </>
              )}
            </div>
            <div className="chart-container">
              <Bar 
                data={{
                  labels: schoolBreakdown.schools.map(s => s.school_name),
                  datasets: [
                    {
                      label: "Enrolment",
                      data: schoolBreakdown.schools.map(s => s.enrolment),
                      backgroundColor: "rgba(102, 126, 234, 0.7)",
                      borderColor: "rgba(102, 126, 234, 1)",
                      borderWidth: 2,
                    },
                    {
                      label: "Graduates",
                      data: schoolBreakdown.schools.map(s => s.graduates),
                      backgroundColor: "rgba(118, 75, 162, 0.7)",
                      borderColor: "rgba(118, 75, 162, 1)",
                      borderWidth: 2,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: "top",
                      labels: {
                        font: { size: 14 },
                        padding: 15,
                      },
                    },
                    tooltip: {
                      callbacks: {
                        label: function (context) {
                          return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                        },
                      },
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        callback: (value) => value.toLocaleString(),
                      },
                      title: {
                        display: true,
                        text: "Number of Students",
                        font: { size: 14, weight: "bold" },
                      },
                    },
                    x: {
                      title: {
                        display: true,
                        text: "School",
                        font: { size: 14, weight: "bold" },
                      },
                      ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45,
                      },
                    },
                  },
                }}
              />
            </div>
          </div>

          <div className="data-table">
            <h3>Detailed Breakdown</h3>
            <table>
              <thead>
                <tr>
                  <th>School Name</th>
                  <th>Enrolment</th>
                  <th>Graduates</th>
                  <th>Completion Rate</th>
                </tr>
              </thead>
              <tbody>
                {schoolBreakdown.schools.map((school, index) => (
                  <tr key={index}>
                    <td>{school.school_name}</td>
                    <td>{school.enrolment.toLocaleString()}</td>
                    <td>{school.graduates.toLocaleString()}</td>
                    <td>
                      {school.completion_rate !== null
                        ? `${school.completion_rate.toFixed(1)}%`
                        : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnrollmentAnalysis;
