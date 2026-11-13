
import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, Legend
} from "recharts";

const API = "https://hr-dashboard-fsan.onrender.com";

const COLORS = ["#2563EB", "#F97316", "#8B5CF6", "#10B981", "#EC4899"];

function App() {
  const [summary, setSummary] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [charts, setCharts] = useState({
    gender_distribution: [],
    attrition_by_department: [],
    income_by_department: [],
    job_satisfaction: []
  });

  const [options, setOptions] = useState({
    departments: ["All"],
    genders: ["All"],
    job_roles: ["All"],
    attritions: ["All"]
  });

  const [filters, setFilters] = useState({
    department: "All",
    gender: "All",
    job_role: "All",
    attrition: "All"
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadFilters() {
    try {
      const response = await fetch(`${API}/filters`);
      if (!response.ok) throw new Error("Unable to load filters");
      setOptions(await response.json());
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadDashboard(selectedFilters = filters) {
    setLoading(true);
    setMessage("");

    try {
      const params = new URLSearchParams();

      Object.entries(selectedFilters).forEach(([key, value]) => {
        if (value !== "All") params.append(key, value);
      });

      const query = params.toString();
      const suffix = query ? `?${query}` : "";

      const [summaryRes, departmentRes, chartsRes] = await Promise.all([
        fetch(`${API}/summary${suffix}`),
        fetch(`${API}/departments${suffix}`),
        fetch(`${API}/charts${suffix}`)
      ]);

      if (!summaryRes.ok || !departmentRes.ok || !chartsRes.ok) {
        throw new Error("Unable to load dashboard data. Please refresh.");
      }

      const summaryData = await summaryRes.json();
      const departmentData = await departmentRes.json();
      const chartsData = await chartsRes.json();

      setSummary(summaryData);
      setDepartments(departmentData);
      setCharts(chartsData);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function changeFilter(name, value) {
    const updatedFilters = {
      ...filters,
      [name]: value
    };

    setFilters(updatedFilters);
    loadDashboard(updatedFilters);
  }

  useEffect(() => {
    loadFilters();
    loadDashboard({
      department: "All",
      gender: "All",
      job_role: "All",
      attrition: "All"
    });
  }, []);

  const attritionData = summary
    ? [
        {
          name: "Active",
          value: summary.total_employees - summary.attrition
        },
        {
          name: "Attrition",
          value: summary.attrition
        }
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

      <section className="filters">
        <div>
          <label>Department</label>
          <select
            value={filters.department}
            onChange={(e) => changeFilter("department", e.target.value)}
          >
            {options.departments.map((item) => (
              <option key={item} value={item}>
                {item === "All" ? "All Departments" : item}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Gender</label>
          <select
            value={filters.gender}
            onChange={(e) => changeFilter("gender", e.target.value)}
          >
            {options.genders.map((item) => (
              <option key={item} value={item}>
                {item === "All" ? "All Genders" : item}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Attrition</label>
          <select
            value={filters.attrition}
            onChange={(e) => changeFilter("attrition", e.target.value)}
          >
            {options.attritions.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Job Role</label>
          <select
            value={filters.job_role}
            onChange={(e) => changeFilter("job_role", e.target.value)}
          >
            {options.job_roles.map((item) => (
              <option key={item} value={item}>
                {item === "All" ? "All Job Roles" : item}
              </option>
            ))}
          </select>
        </div>
      </section>

      {message && <p className="message">{message}</p>}
      {loading && <p>Updating dashboard...</p>}

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
                  <Bar dataKey="employees" fill="#3B82F6" radius={[6, 6, 0, 0]} />
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

            <div className="chart-card">
              <h3>Gender Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={charts.gender_distribution}
                    dataKey="employees"
                    nameKey="gender"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {charts.gender_distribution.map((entry, index) => (
                      <Cell
                        key={entry.gender}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Attrition by Department</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.attrition_by_department}>
                  <XAxis dataKey="department" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="active" name="Active" stackId="a" fill="#10B981" />
                  <Bar dataKey="attrition" name="Attrition" stackId="a" fill="#F97316" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Average Income by Department</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.income_by_department}>
                  <XAxis dataKey="department" />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="average_income"
                    name="Average Income"
                    fill="#8B5CF6"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Job Satisfaction Analysis</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.job_satisfaction}>
                  <XAxis dataKey="satisfaction" />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="employees"
                    name="Employees"
                    fill="#0EA5E9"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
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
