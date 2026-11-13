
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


@app.get("/summary")
def summary():
    if df is None:
        raise HTTPException(status_code=400, detail="Please upload CSV first")

    total = len(df)
    attrition_count = (
        df["Attrition"].astype(str).str.strip().str.lower().isin(["yes", "1", "true"]).sum()
        if "Attrition" in df.columns else 0
    )

    average_income = (
        round(pd.to_numeric(df["Monthly_Income"], errors="coerce").mean(), 2)
        if "Monthly_Income" in df.columns else 0
    )

    return {
        "total_employees": total,
        "attrition": int(attrition_count),
        "attrition_rate": round((attrition_count / total) * 100, 2) if total else 0,
        "average_income": average_income
    }


@app.get("/departments")
def departments():
    if df is None:
        raise HTTPException(status_code=400, detail="Please upload CSV first")

    if "Department" not in df.columns:
        raise HTTPException(status_code=400, detail="Department column not found")

    result = df["Department"].value_counts().reset_index()
    result.columns = ["department", "employees"]
    return result.to_dict(orient="records")
