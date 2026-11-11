
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="HR Analytics Dashboard",
    layout="wide"
)

# Light background for KPIs
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #F0F4F8;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("HR ANALYTICS DASHBOARD")
st.write("Employee Data Analysis")

# Upload CSV
uploaded_file = st.file_uploader(
    "Upload HR Dataset",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # SIDEBAR FILTERS
    st.sidebar.header("Dashboard Filters")

    departments = ["All"] + sorted(
        df["Department"].dropna().unique().tolist()
    )

    selected_department = st.sidebar.selectbox(
        "Department",
        departments
    )

    genders = ["All"] + sorted(
        df["Gender"].dropna().unique().tolist()
    )

    selected_gender = st.sidebar.selectbox(
        "Gender",
        genders
    )

    attrition_options = ["All"] + sorted(
        df["Attrition"].dropna().unique().tolist()
    )

    selected_attrition = st.sidebar.selectbox(
        "Attrition",
        attrition_options
    )

    # APPLY FILTERS
    filtered_df = df.copy()

    if selected_department != "All":
        filtered_df = filtered_df[
            filtered_df["Department"] == selected_department
        ]

    if selected_gender != "All":
        filtered_df = filtered_df[
            filtered_df["Gender"] == selected_gender
        ]

    if selected_attrition != "All":
        filtered_df = filtered_df[
            filtered_df["Attrition"] == selected_attrition
        ]

    # KPI CALCULATIONS
    total_employees = len(filtered_df)

    attrition_count = (
        filtered_df["Attrition"] == "Yes"
    ).sum()

    attrition_rate = (
        attrition_count / total_employees * 100
        if total_employees > 0 else 0
    )

    average_income = (
        filtered_df["Monthly_Income"].mean()
        if total_employees > 0 else 0
    )

    # KPI CARDS
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Employees", f"{total_employees:,}")
    col2.metric("Attrition", f"{attrition_count:,}")
    col3.metric("Attrition Rate", f"{attrition_rate:.1f}%")
    col4.metric("Average Income", f"{average_income:,.0f}")

    st.divider()

    if total_employees > 0:

        # CHART 1
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

        # CHART 2
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

        # CHART 3
        st.subheader("Age Distribution")

        fig3 = px.histogram(
            filtered_df,
            x="Age",
            nbins=15,
            title="Employee Age Distribution"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # CHART 4
        st.subheader("Income by Department")

        fig4 = px.box(
            filtered_df,
            x="Department",
            y="Monthly_Income",
            color="Department"
        )
        st.plotly_chart(fig4, use_container_width=True)

        # CHART 5
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

        # CHART 6
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

        # EMPLOYEE TABLE
        st.subheader("Employee Data")

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        # DOWNLOAD
        st.download_button(
            "Download HR Report",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "HR_Report.csv",
            "text/csv"
        )

    else:
        st.warning("No employees found for the selected filters.")

else:
    st.info("Please upload your HR CSV file.")
