
import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, Legend
} from "recharts";

const API = "https://hr-dashboard-fsan.onrender.com";
const COLORS = ["#2563EB", "#F97316"];

function App() {
  const [summary, setSummary] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);

  async function loadDashboard() {
    setLoading(true);
    setMessage("");

    try {
      const [summaryResponse, departmentResponse] = await Promise.all([
        fetch(`${API}/summary`),
        fetch(`${API}/departments`)
      ]);

      if (!summaryResponse.ok || !departmentResponse.ok) {
        throw new Error("Please upload the HR CSV file first.");
      }

      const summaryData = await summaryResponse.json();
      const departmentData = await departmentResponse.json();

      setSummary(summaryData);
      setDepartments(departmentData);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function uploadCSV() {
    if (!file) {
      setMessage("Please select a CSV file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Upload failed.");
      }

      setMessage("CSV uploaded successfully!");
      await loadDashboard();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const attritionData = summary
    ? [
        { name: "Active", value: summary.total_employees - summary.attrition },
        { name: "Attrition", value: summary.attrition }
      ]
    : [];

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>HR Analytics Dashboard</h1>
          <p>Human Resources Performance Overview</p>
        </div>
        <div className="header-tag">HR ANALYTICS</div>
      </header>

      <section className="upload-card">
        <div>
          <h3>Upload HR Dataset</h3>
          <p>Select your HR CSV file to refresh the dashboard.</p>
        </div>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={uploadCSV} disabled={loading}>
          {loading ? "Please wait..." : "Upload CSV"}
        </button>
        <button className="refresh-button" onClick={loadDashboard}>
          Refresh
        </button>
        {message && <p className="message">{message}</p>}
      </section>

      {loading && !summary && <p>Loading dashboard...</p>}

      {summary && (
        <>
          <section className="kpi-grid">
            <div className="kpi-card blue">
              <p>Total Employees</p>
              <h2>{summary.total_employees.toLocaleString("en-IN")}</h2>
              <span>Workforce size</span>
            </div>

            <div className="kpi-card orange">
              <p>Total Attrition</p>
              <h2>{summary.attrition.toLocaleString("en-IN")}</h2>
              <span>Employees left</span>
            </div>

            <div className="kpi-card purple">
              <p>Attrition Rate</p>
              <h2>{summary.attrition_rate}%</h2>
              <span>Employee turnover</span>
            </div>

            <div className="kpi-card green">
              <p>Average Income</p>
              <h2>{summary.average_income.toLocaleString("en-IN")}</h2>
              <span>Monthly income</span>
            </div>
          </section>

          <section className="charts-grid">
            <div className="chart-card">
              <h3>Employees by Department</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={departments}>
                  <XAxis dataKey="department" />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="employees"
                    fill="#3B82F6"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Employee Attrition</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={attritionData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={95}
                    label
                  >
                    {attritionData.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </section>
        </>
      )}

      <footer>HR Analytics Dashboard | React + FastAPI</footer>
    </div>
  );
}

export default App;
