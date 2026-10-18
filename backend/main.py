import csv
import io
from contextlib import asynccontextmanager
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import ROOT, Evidence, Observation, Source, session
from .research import answer
from .seed import seed


@asynccontextmanager
async def lifespan(app):
    seed()
    yield


app = FastAPI(title="LankaMacro AI", version="0.1.0", lifespan=lifespan)
DB = Annotated[Session, Depends(session)]
Period = Annotated[str | None, Query(pattern=r"^20\d{2}-(0[1-9]|1[0-2])$")]


def source_info(db):
    source = db.get(Source, "dcs-ccpi-2026-09")
    if source is None:
        raise HTTPException(503, "Reviewed corpus not initialized")
    return {**source.metadata_json, "pdf_url": f"/api/sources/{source.id}/pdf"}


def rows_from_db(db):
    rows = {}
    for obs in db.scalars(select(Observation).order_by(Observation.period)):
        rows.setdefault(obs.period, {"period": obs.period})[obs.series] = float(
            obs.value
        )
    return list(rows.values())


def selected_rows(db, start, end):
    rows = rows_from_db(db)
    if start and end and start > end:
        raise HTTPException(422, "Start month must not be after end month")
    if (start and start < rows[0]["period"]) or (end and end > rows[-1]["period"]):
        raise HTTPException(422, "Requested range exceeds reviewed coverage")
    selected = [
        r
        for r in rows
        if (not start or r["period"] >= start) and (not end or r["period"] <= end)
    ]
    if not selected:
        raise HTTPException(404, "No reviewed observations in this range")
    return selected


@app.get("/api/health")
def health(db: DB):
    return {
        "status": "ok",
        "mode": "reviewed-evidence-baseline",
        "coverage": {"start": "2025-09", "end": "2026-09"},
        "source": source_info(db),
    }


@app.get("/api/sources")
def sources(db: DB):
    return {
        "sources": [source_info(db)],
        "evidence": [
            e.metadata_json for e in db.scalars(select(Evidence).order_by(Evidence.id))
        ],
    }


@app.get("/api/sources/{source_id}/pdf")
def source_pdf(source_id: str, db: DB):
    if source_id != "dcs-ccpi-2026-09":
        raise HTTPException(404, "Unknown reviewed source")
    source = source_info(db)
    return FileResponse(
        ROOT / "data/sources" / source["file"],
        media_type="application/pdf",
        content_disposition_type="inline",
        filename=source["file"],
    )


@app.get("/api/series")
def series(db: DB, start: Period = None, end: Period = None):
    return {
        "rows": selected_rows(db, start, end),
        "source": source_info(db),
        "units": {
            "headline": "% year-on-year",
            "food": "% year-on-year",
            "non_food": "% year-on-year",
            "index": "index points; 2021=100",
        },
    }


@app.get("/api/series.csv")
def series_csv(db: DB, start: Period = None, end: Period = None):
    rows = selected_rows(db, start, end)
    source = source_info(db)
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerow(
        [
            "period",
            "headline_yoy_percent",
            "food_yoy_percent",
            "non_food_yoy_percent",
            "ccpi_index_2021_100",
            "source_url",
            "source_page",
            "release_date",
            "reviewed_on",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r["period"],
                r["headline"],
                r["food"],
                r["non_food"],
                r["index"],
                source["url"],
                source["page"],
                source["release_date"],
                source["reviewed_on"],
            ]
        )
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=lankamacro-ccpi.csv"},
    )


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=1200)


@app.post("/api/chat")
def chat(body: Question, db: DB):
    if not body.question.strip():
        raise HTTPException(422, "Question cannot be blank")
    source = source_info(db)
    evidence = [e.metadata_json for e in db.scalars(select(Evidence))]
    evidence.sort(key=lambda x: x["id"] != "inflation-definition")
    return answer(body.question, rows_from_db(db), evidence, source)


class Scenario(BaseModel):
    principal: Decimal = Field(
        ge=1, le=1_000_000_000_000, max_digits=16, decimal_places=2
    )
    nominal_rate: Decimal = Field(ge=-99, le=100, max_digits=8, decimal_places=4)
    inflation_rate: Decimal = Field(ge=-99, le=100, max_digits=8, decimal_places=4)
    years: int = Field(ge=1, le=30)


@app.post("/api/scenarios/real-return")
def scenario(body: Scenario):
    with localcontext() as context:
        context.prec = 120
        return calculate_scenario(body)


def calculate_scenario(body: Scenario):
    nominal_factor = 1 + body.nominal_rate / 100
    inflation_factor = 1 + body.inflation_rate / 100
    nominal = body.principal * nominal_factor**body.years
    real = nominal / inflation_factor**body.years
    money = lambda n: str(n.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {
        "nominal_value": money(nominal),
        "real_value": money(real),
        "real_annual_rate": str(
            ((nominal_factor / inflation_factor - 1) * 100).quantize(Decimal("0.0001"))
        ),
        "real_gain": money(real - body.principal),
        "currency": "LKR",
        "assumptions": [
            "Constant annual rates with annual compounding",
            "No tax, fees, contributions or withdrawals",
            "Inflation is a user-specified scenario, not a forecast",
        ],
        "formula": "real value = principal × ((1 + nominal rate/100) / (1 + inflation rate/100))^years",
    }
