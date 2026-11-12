from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "manas_random_forest.pkl"
STATIC_DIR = BASE_DIR / "static"

FEATURE_NAMES = [
    "Age",
    "Gender",
    "Country",
    "Academic_Level",
    "Most_Used_Platform",
    "Purpose_Of_Use",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Study_Hours",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night",
    "Stress_Level",
]

model = None


class AssessmentInput(BaseModel):
    """Input fields expected by the trained pipeline."""

    age: float = Field(..., alias="Age", ge=1, le=120)
    gender: Literal["Female", "Male"] = Field(..., alias="Gender")
    country: Literal[
        "Australia",
        "Bangladesh",
        "Brazil",
        "Canada",
        "China",
        "Denmark",
        "Finland",
        "France",
        "Germany",
        "India",
        "Ireland",
        "Italy",
        "Japan",
        "Malaysia",
        "Maldives",
        "Mexico",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Other",
        "Pakistan",
        "Poland",
        "Russia",
        "Singapore",
        "South Korea",
        "Spain",
        "Sri Lanka",
        "Switzerland",
        "Turkey",
        "UAE",
        "UK",
        "USA",
    ] = Field(..., alias="Country")
    academic_level: Literal["Graduate", "High School", "Undergraduate"] = Field(
        ..., alias="Academic_Level"
    )
    most_used_platform: Literal[
        "Facebook",
        "Instagram",
        "KakaoTalk",
        "LINE",
        "LinkedIn",
        "Snapchat",
        "TikTok",
        "Twitter",
        "VKontakte",
        "WeChat",
        "WhatsApp",
        "YouTube",
    ] = Field(..., alias="Most_Used_Platform")
    purpose_of_use: Literal[
        "Education", "Entertainment", "Networking", "News"
    ] = Field(..., alias="Purpose_Of_Use")
    avg_daily_usage_hours: float = Field(
        ..., alias="Avg_Daily_Usage_Hours", ge=0, le=24
    )
    daily_unlocks: float = Field(..., alias="Daily_Unlocks", ge=0, le=1000)
    study_hours: float = Field(..., alias="Study_Hours", ge=0, le=24)
    physical_activity_hours: float = Field(
        ..., alias="Physical_Activity_Hours", ge=0, le=24
    )
    sleep_hours_per_night: float = Field(
        ..., alias="Sleep_Hours_Per_Night", ge=0, le=24
    )
    stress_level: Literal["High", "Low", "Medium", "Very High"] = Field(
        ..., alias="Stress_Level"
    )

    class Config:
        populate_by_name = True


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load the existing model once when the application starts."""

    global model
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file was not found: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(title="MANAS Mental Health Scoring", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/predict")
async def predict_score(payload: AssessmentInput) -> dict[str, float]:
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="The prediction model is not loaded. Please try again shortly.",
        )

    values = payload.model_dump(by_alias=True)
    input_frame = pd.DataFrame([values], columns=FEATURE_NAMES)

    try:
        prediction = float(model.predict(input_frame)[0])
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error

    return {"Mental_Health_Score": round(prediction, 2)}
