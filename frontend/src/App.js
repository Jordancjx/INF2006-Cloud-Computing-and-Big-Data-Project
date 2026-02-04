import React, { useState } from "react";
import "./App.css";
import EmploymentTrends from "./components/EmploymentTrends";
import SalaryCorrelation from "./components/SalaryCorrelation";
import EnrollmentAnalysis from "./components/EnrollmentAnalysis";

function App() {
  const [activeTab, setActiveTab] = useState("employment");

  return (
    <div className="App">
      <header className="app-header">
        <h1>Education Analytics Dashboard</h1>
        <p>Ministry of Education Singapore - Data Analytics Platform</p>
      </header>

      <nav className="analytics-nav">
        <button
          className={activeTab === "employment" ? "active" : ""}
          onClick={() => setActiveTab("employment")}
        >
          Employment Trends
        </button>
        <button
          className={activeTab === "salary" ? "active" : ""}
          onClick={() => setActiveTab("salary")}
        >
          Salary Correlation
        </button>
        <button
          className={activeTab === "enrollment" ? "active" : ""}
          onClick={() => setActiveTab("enrollment")}
        >
          Enrollment Analysis
        </button>
      </nav>

      <main className="analytics-content">
        {activeTab === "employment" && <EmploymentTrends />}
        {activeTab === "salary" && <SalaryCorrelation />}
        {activeTab === "enrollment" && <EnrollmentAnalysis />}
      </main>

      <footer className="app-footer">
        <p>Done by Mr Getgo Jordan Chan Jun Xiang</p>
      </footer>
    </div>
  );
}

export default App;
