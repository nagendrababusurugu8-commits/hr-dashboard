
import React from "react";
import {
  ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, Legend
} from "recharts";

const departmentData = [
  { name: "Sales", employees: 850 },
  { name: "IT", employees: 720 },
  { name: "HR", employees: 420 },
  { name: "Finance", employees: 610 },
  { name: "Operations", employees: 800 }
];

const attritionData = [
  { name: "Active", value: 1676 },
  { name: "Attrition", value: 1724 }
];

const COLORS = ["#2563EB", "#F97316"];

function App() {
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
          <select><option>All Departments</option></select>
        </div>
        <div>
          <label>Gender</label>
          <select><option>All Genders</option></select>
        </div>
        <div>
          <label>Attrition</label>
          <select><option>All</option></select>
        </div>
        <div>
          <label>Job Role</label>
          <select><option>All Job Roles</option></select>
        </div>
      </section>

      <section className="kpi-grid">
        <div className="kpi-card blue">
          <p>Total Employees</p>
          <h2>3,400</h2>
          <span>Workforce size</span>
        </div>
        <div className="kpi-card orange">
          <p>Total Attrition</p>
          <h2>1,724</h2>
          <span>Employees left</span>
        </div>
        <div className="kpi-card purple">
          <p>Attrition Rate</p>
          <h2>50.7%</h2>
          <span>Employee turnover</span>
        </div>
        <div className="kpi-card green">
          <p>Average Income</p>
          <h2>5,125</h2>
          <span>Monthly income</span>
        </div>
      </section>

      <section className="charts-grid">
        <div className="chart-card">
          <h3>Employees by Department</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={departmentData}>
              <XAxis dataKey="name" />
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
      </section>

      <footer>
        HR Analytics Dashboard | React + FastAPI
      </footer>
    </div>
  );
}

export default App;
