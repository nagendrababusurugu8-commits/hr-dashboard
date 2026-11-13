
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
