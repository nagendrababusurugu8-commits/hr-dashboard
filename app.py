
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide"
)

# ---------------- KPI STYLING ----------------
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #F0F4F8;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #DCE3EA;
}
</style>
""", unsafe_allow_html=True)

st.title("👥 HR ANALYTICS DASHBOARD")
st.caption("Employee Data Analysis")

# ---------------- CACHED DATA LOADING ----------------
@st.cache_data(show_spinner="Loading HR dataset...")
def load_data(file_bytes):
    data = pd.read_csv(BytesIO(file_bytes))

    data.columns = (
        data.columns.astype(str)
        .str.strip()
    )

    # Support common column naming variations
    rename_map = {
        "JobRole": "Job_Role",
        "JobSatisfaction": "Job_Satisfaction",
        "MonthlyIncome": "Monthly_Income"
    }

    for old, new in rename_map.items():
        if old in data.columns and new not in data.columns:
            data = data.rename(columns={old: new})

    required = [
        "Department",
        "Gender",
        "Attrition",
        "Monthly_Income",
        "Age",
        "Job_Satisfaction"
    ]

    missing = [c for c in required if c not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in ["Monthly_Income", "Age", "Job_Satisfaction"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    for col in ["Department", "Gender", "Attrition"]:
        data[col] = data[col].fillna("Unknown").astype(str)

    if "Job_Role" in data.columns:
        data["Job_Role"] = data["Job_Role"].fillna("Unknown").astype(str)

    return data


# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload HR Dataset",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = load_data(uploaded_file.getvalue())

    except Exception as e:
        st.error(f"File loading error: {e}")
        st.stop()

    if df.empty:
        st.warning("No employee records found.")
        st.stop()

    # ---------------- SIDEBAR SLICERS ----------------
    st.sidebar.header("📌 Dashboard Slicers")

    # 1. Department + Search
    st.sidebar.subheader("Department Search")

    department_search = st.sidebar.text_input(
        "Search Department",
        placeholder="Type department..."
    )

    all_departments = sorted(df["Department"].unique().tolist())

    if department_search:
        department_options = [
            x for x in all_departments
            if department_search.casefold() in x.casefold()
        ]
    else:
        department_options = all_departments

    selected_departments = st.sidebar.multiselect(
        "Department",
        options=department_options,
        default=[]
    )

    # 2. Gender
    genders = sorted(df["Gender"].unique().tolist())

    selected_genders = st.sidebar.multiselect(
        "Gender",
        options=genders,
        default=genders
    )

    # 3. Attrition
    attrition_options = sorted(df["Attrition"].unique().tolist())

    selected_attrition = st.sidebar.multiselect(
        "Attrition",
        options=attrition_options,
        default=attrition_options
    )

    # 4. Job Role + Search
    if "Job_Role" in df.columns:

        st.sidebar.subheader("Job Role Search")

        role_search = st.sidebar.text_input(
            "Search Job Role",
            placeholder="Type job role..."
        )

        all_roles = sorted(df["Job_Role"].unique().tolist())

        if role_search:
            role_options = [
                x for x in all_roles
                if role_search.casefold() in x.casefold()
            ]
        else:
            role_options = all_roles

        selected_roles = st.sidebar.multiselect(
            "Job Role",
            options=role_options,
            default=[]
        )

    else:
        selected_roles = []

    # 5. Job Satisfaction
    satisfaction_options = sorted(
        df["Job_Satisfaction"].dropna().unique().tolist()
    )

    selected_satisfaction = st.sidebar.multiselect(
        "Job Satisfaction",
        options=satisfaction_options,
        default=satisfaction_options
    )

    # 6. Age Range
    age_values = df["Age"].dropna()

    if not age_values.empty:
        min_age = int(age_values.min())
        max_age = int(age_values.max())

        if min_age < max_age:
            age_range = st.sidebar.slider(
                "Age Range",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age)
            )
        else:
            age_range = (min_age, max_age)
            st.sidebar.write("Age Range:", age_range)
    else:
        age_range = (0, 100)

    # 7. Monthly Income Range
    income_values = df["Monthly_Income"].dropna()

    if not income_values.empty:
        min_income = float(income_values.min())
        max_income = float(income_values.max())

        if min_income < max_income:
            income_range = st.sidebar.slider(
                "Monthly Income Range",
                min_value=min_income,
                max_value=max_income,
                value=(min_income, max_income),
                format="%.0f"
            )
        else:
            income_range = (min_income, max_income)
            st.sidebar.write("Income Range:", income_range)
    else:
        income_range = (0.0, 0.0)

    # ---------------- FAST FILTERING ----------------
    mask = pd.Series(True, index=df.index)

    if selected_departments:
        mask &= df["Department"].isin(selected_departments)

    mask &= df["Gender"].isin(selected_genders)

    mask &= df["Attrition"].isin(selected_attrition)

    if "Job_Role" in df.columns and selected_roles:
        mask &= df["Job_Role"].isin(selected_roles)

    mask &= df["Job_Satisfaction"].isin(selected_satisfaction)

    mask &= df["Age"].between(
        age_range[0],
        age_range[1]
    )

    mask &= df["Monthly_Income"].between(
        income_range[0],
        income_range[1]
    )

    filtered_df = df.loc[mask]

    # ---------------- KPI SECTION ----------------
    st.subheader("📊 Key Performance Indicators")

    total_employees = len(filtered_df)

    attrition_count = (
        filtered_df["Attrition"].str.strip().str.casefold() == "yes"
    ).sum()

    attrition_rate = (
        attrition_count / total_employees * 100
        if total_employees > 0 else 0
    )

    average_income = (
        filtered_df["Monthly_Income"].mean()
        if total_employees > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Employees", f"{total_employees:,}")
    col2.metric("Attrition", f"{attrition_count:,}")
    col3.metric("Attrition Rate", f"{attrition_rate:.1f}%")
    col4.metric("Average Income", f"{average_income:,.0f}")

    st.caption(
        f"Showing {total_employees:,} employees out of {len(df):,} records"
    )

    st.divider()

    if filtered_df.empty:

        st.warning("No employees found for the selected filters.")

    else:

        # ---------------- CHART 1 ----------------
        st.subheader("Employees by Department")

        dept_data = (
            filtered_df["Department"]
            .value_counts()
            .reset_index()
        )

        dept_data.columns = ["Department", "Employees"]

        fig1 = px.bar(
            dept_data,
            x="Department",
            y="Employees",
            color="Department",
            title="Department-wise Employees"
        )

        st.plotly_chart(fig1, use_container_width=True)

        # ---------------- CHART 2 ----------------
        st.subheader("Attrition Analysis")

        attr_data = (
            filtered_df["Attrition"]
            .value_counts()
            .reset_index()
        )

        attr_data.columns = ["Attrition", "Employees"]

        fig2 = px.pie(
            attr_data,
            names="Attrition",
            values="Employees",
            hole=0.4
        )

        st.plotly_chart(fig2, use_container_width=True)

        # ---------------- CHART 3 ----------------
        st.subheader("Age Distribution")

        fig3 = px.histogram(
            filtered_df,
            x="Age",
            nbins=15,
            title="Employee Age Distribution"
        )

        st.plotly_chart(fig3, use_container_width=True)

        # ---------------- CHART 4 ----------------
        st.subheader("Income by Department")

        fig4 = px.box(
            filtered_df,
            x="Department",
            y="Monthly_Income",
            color="Department"
        )

        st.plotly_chart(fig4, use_container_width=True)

        # ---------------- CHART 5 ----------------
        st.subheader("Gender Distribution")

        gender_data = (
            filtered_df["Gender"]
            .value_counts()
            .reset_index()
        )

        gender_data.columns = ["Gender", "Employees"]

        fig5 = px.pie(
            gender_data,
            names="Gender",
            values="Employees",
            hole=0.4
        )

        st.plotly_chart(fig5, use_container_width=True)

        # ---------------- CHART 6 ----------------
        st.subheader("Job Satisfaction Analysis")

        satisfaction_data = (
            filtered_df.groupby("Job_Satisfaction")
            .size()
            .reset_index(name="Employees")
        )

        fig6 = px.bar(
            satisfaction_data,
            x="Job_Satisfaction",
            y="Employees",
            title="Employees by Job Satisfaction"
        )

        st.plotly_chart(fig6, use_container_width=True)

    # ---------------- EMPLOYEE TABLE ----------------
    st.subheader("📋 Employee Data")

    show_all = st.checkbox("Show all filtered employees")

    if show_all:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
    else:
        st.dataframe(
            filtered_df.head(1000),
            use_container_width=True,
            height=400
        )

        if len(filtered_df) > 1000:
            st.caption("Showing first 1,000 rows. Download for complete data.")

    # ---------------- DOWNLOAD ----------------
    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download HR Report",
        data=csv,
        file_name="HR_Report.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload your HR CSV file.")
