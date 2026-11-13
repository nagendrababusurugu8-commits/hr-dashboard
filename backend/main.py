
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO

app = FastAPI(title="HR Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = None


@app.get("/")
def home():
    return {"message": "HR Dashboard API is running"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    global df

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        return {
            "message": "CSV uploaded successfully",
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def filtered_data(department=None, gender=None, job_role=None, attrition=None):
    if df is None:
        raise HTTPException(status_code=400, detail="Please upload CSV first")

    data = df.copy()

    if department and department != "All":
        data = data[data["Department"].astype(str) == department]

    if gender and gender != "All":
        data = data[data["Gender"].astype(str) == gender]

    if job_role and job_role != "All":
        data = data[data["Job_Role"].astype(str) == job_role]

    if attrition and attrition != "All":
        data = data[data["Attrition"].astype(str) == attrition]

    return data


@app.get("/summary")
def summary(
    department: str = None,
    gender: str = None,
    job_role: str = None,
    attrition: str = None
):
    data = filtered_data(department, gender, job_role, attrition)

    total = len(data)
    attrition_count = (
        data["Attrition"].astype(str).str.strip().str.lower()
        .isin(["yes", "1", "true"]).sum()
    )

    average_income = pd.to_numeric(
        data["Monthly_Income"], errors="coerce"
    ).mean()

    return {
        "total_employees": total,
        "attrition": int(attrition_count),
        "attrition_rate": round(attrition_count / total * 100, 2) if total else 0,
        "average_income": round(float(average_income), 2) if pd.notna(average_income) else 0
    }


@app.get("/departments")
def departments(
    department: str = None,
    gender: str = None,
    job_role: str = None,
    attrition: str = None
):
    data = filtered_data(department, gender, job_role, attrition)

    result = data["Department"].value_counts().reset_index()
    result.columns = ["department", "employees"]
    return result.to_dict(orient="records")


@app.get("/filters")
def filters():
    if df is None:
        raise HTTPException(status_code=400, detail="Please upload CSV first")

    return {
        "departments": ["All"] + sorted(df["Department"].dropna().astype(str).unique().tolist()),
        "genders": ["All"] + sorted(df["Gender"].dropna().astype(str).unique().tolist()),
        "job_roles": ["All"] + sorted(df["Job_Role"].dropna().astype(str).unique().tolist()),
        "attritions": ["All"] + sorted(df["Attrition"].dropna().astype(str).unique().tolist())
    }

@app.get("/charts")
def charts(
    department: str = None,
    gender: str = None,
    job_role: str = None,
    attrition: str = None
):
    data = filtered_data(department, gender, job_role, attrition)

    # 1. Gender Distribution
    gender_data = (
        data["Gender"].value_counts()
        .rename_axis("gender")
        .reset_index(name="employees")
        .to_dict(orient="records")
    )

    # 2. Attrition by Department
    temp = data.copy()
    temp["attrition_flag"] = (
        temp["Attrition"].astype(str).str.strip().str.lower()
        .isin(["yes", "1", "true"])
    )

    attrition_data = (
        temp.groupby("Department")
        .agg(
            attrition=("attrition_flag", "sum"),
            total=("attrition_flag", "count")
        )
        .reset_index()
    )

    attrition_data["active"] = (
        attrition_data["total"] - attrition_data["attrition"]
    )
    attrition_data = attrition_data.rename(
        columns={"Department": "department"}
    )

    # 3. Average Income by Department
    income_data = data.copy()
    income_data["Monthly_Income"] = pd.to_numeric(
        income_data["Monthly_Income"], errors="coerce"
    )

    income_data = (
        income_data.groupby("Department")["Monthly_Income"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={
            "Department": "department",
            "Monthly_Income": "average_income"
        })
        .to_dict(orient="records")
    )

    # 4. Job Satisfaction
    satisfaction_data = (
        data["Job_Satisfaction"].value_counts()
        .sort_index()
        .rename_axis("satisfaction")
        .reset_index(name="employees")
        .to_dict(orient="records")
    )

    return {
        "gender_distribution": gender_data,
        "attrition_by_department": attrition_data.to_dict(orient="records"),
        "income_by_department": income_data,
        "job_satisfaction": satisfaction_data
    }
