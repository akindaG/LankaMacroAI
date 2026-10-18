import csv
import hashlib
import io
import json

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.database import ROOT, Observation, Source
from backend.ingest import stage
from backend.seed import seed


def test_original_source_and_transcription():
    snapshot = json.loads((ROOT / "data/inflation.json").read_text())
    pdf = ROOT / "data/sources" / snapshot["source"]["file"]
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == snapshot["source"]["sha256"]
    rows = snapshot["observations"]
    assert len(rows) == 13
    assert rows[0] == {
        "period": "2025-09",
        "headline": 1.5,
        "food": 2.9,
        "non_food": 0.7,
        "index": 193.7,
    }
    assert rows[-1] == {
        "period": "2026-09",
        "headline": 8.0,
        "food": 8.7,
        "non_food": 7.7,
        "index": 209.1,
    }


def test_idempotent_publication(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'seed.db'}")
    seed(engine)
    seed(engine)
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 52
        assert db.scalar(select(func.count()).select_from(Source)) == 1


def test_health_and_source_metadata(client):
    result = client.get("/api/health").json()
    assert result["status"] == "ok"
    assert "Census and Statistics" in result["source"]["publisher"]
    assert result["source"]["page"] == 4
    assert len(client.get("/api/sources").json()["evidence"]) == 3


def test_filter_csv_provenance_and_pdf(client):
    rows = client.get("/api/series?start=2026-08&end=2026-09").json()["rows"]
    assert [r["period"] for r in rows] == ["2026-08", "2026-09"]
    response = client.get("/api/series.csv?start=2026-08&end=2026-09")
    parsed = list(csv.DictReader(io.StringIO(response.text)))
    assert len(parsed) == 2
    assert parsed[-1]["source_page"] == "4"
    assert parsed[-1]["food_yoy_percent"] == "8.7"
    pdf = client.get("/api/sources/dcs-ccpi-2026-09/pdf")
    assert pdf.content.startswith(b"%PDF")
    assert "inline" in pdf.headers["content-disposition"]
    assert client.get("/api/sources/unknown/pdf").status_code == 404


@pytest.mark.parametrize(
    "path,status",
    [
        ("/api/series?start=2026-09&end=2026-08", 422),
        ("/api/series?start=2024-01", 422),
        ("/api/series?end=2027-01", 422),
        ("/api/series?start=2026-13", 422),
        ("/api/series?start=2027-01", 404),
    ],
)
def test_unavailable_and_invalid_ranges(client, path, status):
    assert client.get(path).status_code == status


@pytest.mark.parametrize(
    "question",
    [
        "What is NCPI inflation?",
        "Show core inflation",
        "What will inflation be next year?",
        "GDP growth in 2026",
        "Why did inflation rise?",
        "Show inflation January 2025",
        "Show inflation October 2026",
        "Inflation in 2027",
        "Show inflation in September",
        "What is the annual average inflation?",
        "What is month-on-month inflation?",
        "Should I invest in stocks?",
    ],
)
def test_no_unsupported_claims(client, question):
    result = client.post("/api/chat", json={"question": question}).json()
    assert result["status"] == "insufficient_evidence"
    assert result["citations"] == []
    assert result["chart"] is None


@pytest.mark.parametrize(
    "question,expected,series",
    [
        (
            "Compare inflation September 2025 and September 2026",
            "+6.5 percentage points",
            "headline",
        ),
        (
            "Show food inflation August 2026 to September 2026",
            "+0.2 percentage points",
            "food",
        ),
        ("Show non-food inflation September 2026", "7.7%", "non_food"),
        (
            "Compare CCPI index September 2025 and September 2026",
            "+15.4 index points",
            "index",
        ),
        ("Show inflation 2026-02", "1.6%", "headline"),
        ("Latest inflation", "8.0%", "headline"),
    ],
)
def test_grounded_numeric_answers(client, question, expected, series):
    result = client.post("/api/chat", json={"question": question}).json()
    assert result["status"] == "answered"
    assert expected in result["answer"]
    assert result["chart"]["series"] == [series]
    assert result["citations"][0]["page"] == 4


def test_definition_and_partial_year_are_distinct(client):
    definition = client.post(
        "/api/chat", json={"question": "What is year-on-year inflation?"}
    ).json()
    assert "previous 12 months" in definition["answer"]
    assert definition["chart"] is None
    result = client.post(
        "/api/chat", json={"question": "Show inflation in 2026"}
    ).json()
    assert len(result["chart"]["rows"]) == 9
    assert "not a full-year average" in result["answer"]


def test_scenario_exact_real_return_and_deflation(client):
    result = client.post(
        "/api/scenarios/real-return",
        json={
            "principal": "100000",
            "nominal_rate": "10",
            "inflation_rate": "8",
            "years": 1,
        },
    ).json()
    assert result["nominal_value"] == "110000.00"
    assert result["real_value"] == "101851.85"
    assert result["real_annual_rate"] == "1.8519"
    deflation = client.post(
        "/api/scenarios/real-return",
        json={
            "principal": "100",
            "nominal_rate": "0",
            "inflation_rate": "-2",
            "years": 2,
        },
    ).json()
    assert deflation["real_value"] == "104.12"


@pytest.mark.parametrize(
    "override",
    [
        {"principal": "-1"},
        {"inflation_rate": "-100"},
        {"nominal_rate": "NaN"},
        {"years": 0},
        {"years": 1.5},
        {"principal": "Infinity"},
    ],
)
def test_scenario_validation(client, override):
    body = {
        "principal": "100000",
        "nominal_rate": "10",
        "inflation_rate": "8",
        "years": 1,
    } | override
    assert client.post("/api/scenarios/real-return", json=body).status_code == 422


def test_scenario_at_permitted_extremes(client):
    result = client.post(
        "/api/scenarios/real-return",
        json={
            "principal": "1000000000000",
            "nominal_rate": "100",
            "inflation_rate": "-99",
            "years": 30,
        },
    )
    assert result.status_code == 200
    assert result.json()["real_value"] == str(10**12 * 200**30) + ".00"


def test_scanned_pdf_requires_review_and_does_not_publish(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.ingest.ROOT", tmp_path)
    result = stage(
        ROOT / "data/sources/ccpi-september-2026.pdf",
        "CCPI",
        "DCS",
        "https://www.statistics.gov.lk/",
    )
    record = json.loads((result / "extraction.json").read_text())
    assert record["status"] == "needs_ocr_and_review"
    assert len(record["pages"]) == 8
    assert not (tmp_path / "data/inflation.json").exists()
