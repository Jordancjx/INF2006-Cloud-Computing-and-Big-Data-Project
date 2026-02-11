import React, { useState, useEffect } from "react";
import { Scatter, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  CategoryScale,
  Tooltip,
  Legend,
} from "chart.js";
import "./SalaryCorrelation.css";

ChartJS.register(LinearScale, PointElement, LineElement, CategoryScale, Tooltip, Legend);

const SalaryCorrelation = () => {
  const [selectedYear, setSelectedYear] = useState(2022);
  const [selectedSchool, setSelectedSchool] = useState("");
  const [viewMode, setViewMode] = useState('scatter'); // 'scatter' or 'trends'
  const [selectedDegree, setSelectedDegree] = useState(null);
  const [degreeHistoricalData, setDegreeHistoricalData] = useState(null);
  const [loadingTrends, setLoadingTrends] = useState(false);

  // Color palette for different schools
  const schoolColors = {
    "Nanyang Technological University": "#D8232A",
    "National University of Singapore": "#003D7C",
    "Singapore Management University": "#0077BE",
    "Singapore University of Technology and Design": "#FF6E1B",
    "Singapore Institute of Technology": "#6A1E55",
    "Singapore University of Social Sciences": "#00A94F",
    "Nanyang Polytechnic": "#8B4789",
    "Singapore Polytechnic": "#E31837",
    "Temasek Polytechnic": "#0056A5",
    "Republic Polytechnic": "#009639",
    "Ngee Ann Polytechnic": "#8C1D40",
    "LASALLE College of the Arts (Degree)": "#FFD700",
    "Nanyang Academy of Fine Arts (Degree)": "#FF9500",
    "National Institute of Education": "#3B5998",
    "Institute of Technical Education": "#7D3C98",
  };

  const getSchoolColor = (schoolName) => {
    return schoolColors[schoolName] || "#667EA4"; // Default color if school not in palette
  };

  // Convert hex color to rgba with transparency
  const hexToRgba = (hex, alpha = 0.6) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

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

  // Fetch degree historical trends when a point is clicked
  const fetchDegreeHistoricalTrends = async (degreeName, schoolName) => {
    setLoadingTrends(true);
    setViewMode('trends');
    setSelectedDegree({ name: degreeName, school: schoolName });
    
    try {
      let url = `${API_BASE_URL}/api/analytics/degree-historical-trends?degree=${encodeURIComponent(degreeName)}`;
      if (selectedSchool) {
        url += `&school=${encodeURIComponent(selectedSchool)}`;
      }
      
      const response = await fetch(url);
      const result = await response.json();
      
      if (result.success) {
        setDegreeHistoricalData(result.data);
      } else {
        alert(`No historical data available for ${degreeName}`);
        setViewMode('scatter');
      }
    } catch (err) {
      console.error("Error fetching degree trends:", err);
      setViewMode('scatter');
    } finally {
      setLoadingTrends(false);
    }
  };

  // Go back to scatter view
  const backToScatter = () => {
    setViewMode('scatter');
    setSelectedDegree(null);
    setDegreeHistoricalData(null);
  };

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

  // Prepare scatter plot data - group by school for coloring
  const groupedBySchool = {};
  data.data.forEach((item) => {
    const school = item.school || "Other";
    if (!groupedBySchool[school]) {
      groupedBySchool[school] = [];
    }
    groupedBySchool[school].push(item);
  });

  const scatterData = {
    datasets: Object.keys(groupedBySchool).map((school) => ({
      label: school,
      data: groupedBySchool[school].map((item) => ({
        x: item.median_salary,
        y: item.employment_rate,
        degree: item.degree,
        school: item.school,
      })),
      backgroundColor: hexToRgba(getSchoolColor(school), 0.6),
      borderColor: getSchoolColor(school),
      pointRadius: 8,
      pointHoverRadius: 10,
    })),
  };

  const scatterOptions = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const datasetIndex = elements[0].datasetIndex;
        const index = elements[0].index;
        const point = scatterData.datasets[datasetIndex].data[index];
        fetchDegreeHistoricalTrends(point.degree, point.school);
      }
    },
    plugins: {
      legend: { display: true, position: "top" },
      tooltip: {
        callbacks: {
          label: function (context) {
            const point = context.raw;
            return [
              `Degree: ${point.degree}`,
              `School: ${point.school}`,
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
        {viewMode === 'trends' && (
          <button className="back-btn" onClick={backToScatter}>
            ← Back to Scatter Plot
          </button>
        )}
        <h3>
          {viewMode === 'scatter'
            ? 'Salary vs Employment Rate by Degree'
            : `Historical Trends: ${selectedDegree?.name}`}
        </h3>
        {viewMode === 'trends' && degreeHistoricalData && (
          <div className="degree-info">
            <p><strong>School:</strong> {selectedDegree?.school || 'All Schools'}</p>
            {degreeHistoricalData.schools_offering && degreeHistoricalData.schools_offering.length > 1 && !selectedSchool && (
              <p><strong>Also offered by:</strong> {degreeHistoricalData.schools_offering.filter(s => s !== selectedDegree?.school).join(', ')}</p>
            )}
            {degreeHistoricalData.trends && degreeHistoricalData.trends.length > 0 && (
              <p><strong>Data available:</strong> {degreeHistoricalData.trends[0].year} - {degreeHistoricalData.trends[degreeHistoricalData.trends.length - 1].year} ({degreeHistoricalData.trends.length} years)</p>
            )}
          </div>
        )}
        {viewMode === 'scatter' && (
          <p className="chart-hint">💡 Click on any point to see historical trends for that degree</p>
        )}
        <div className="chart-container">
          {loadingTrends ? (
            <div className="loading-breakdown">
              <div className="spinner"></div>
              <p>Loading historical data...</p>
            </div>
          ) : viewMode === 'scatter' ? (
            <Scatter data={scatterData} options={scatterOptions} />
          ) : degreeHistoricalData && degreeHistoricalData.trends ? (
            <Line
              data={{
                labels: degreeHistoricalData.trends.map((t) => t.year),
                datasets: [
                  {
                    label: 'Median Salary ($)',
                    data: degreeHistoricalData.trends.map((t) => t.median_salary),
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    yAxisID: 'y',
                    tension: 0.3,
                    pointRadius: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? 10 : 5
                    ),
                    pointBorderWidth: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? 3 : 1
                    ),
                    pointBackgroundColor: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? '#FF5722' : '#4CAF50'
                    ),
                  },
                  {
                    label: 'Employment Rate (%)',
                    data: degreeHistoricalData.trends.map((t) => t.employment_rate),
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.3,
                    pointRadius: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? 10 : 5
                    ),
                    pointBorderWidth: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? 3 : 1
                    ),
                    pointBackgroundColor: degreeHistoricalData.trends.map((t) =>
                      t.year === selectedYear ? '#FF5722' : '#2196F3'
                    ),
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                  mode: 'index',
                  intersect: false,
                },
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  tooltip: {
                    callbacks: {
                      afterLabel: (context) => {
                        if (context.parsed.x === selectedYear) {
                          return '← Current Year';
                        }
                        return '';
                      },
                    },
                  },
                },
                scales: {
                  y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                      display: true,
                      text: 'Median Salary ($)',
                      font: { weight: 'bold' },
                    },
                    ticks: {
                      callback: (value) => `$${value}`,
                    },
                  },
                  y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                      display: true,
                      text: 'Employment Rate (%)',
                      font: { weight: 'bold' },
                    },
                    grid: {
                      drawOnChartArea: false,
                    },
                    ticks: {
                      callback: (value) => `${value}%`,
                    },
                  },
                },
              }}
            />
          ) : null}
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