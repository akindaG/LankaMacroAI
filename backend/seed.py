"""Publish the checked snapshot. Ingestion staging never calls this automatically."""

import hashlib
import json

from sqlalchemy.orm import Session

from .database import ROOT, Base, Evidence, Observation, Source, engine


def seed(db_engine=engine):
    snapshot = json.loads((ROOT / "data/inflation.json").read_text())
    source = snapshot["source"]
    file = ROOT / "data/sources" / source["file"]
    if hashlib.sha256(file.read_bytes()).hexdigest() != source["sha256"]:
        raise ValueError("Reviewed source checksum mismatch; publication refused")
    Base.metadata.create_all(db_engine)
    with Session(db_engine) as db, db.begin():
        db.merge(Source(id=source["id"], metadata_json=source))
        db.flush()
        for row in snapshot["observations"]:
            for series, value in row.items():
                if series != "period":
                    db.merge(
                        Observation(
                            period=row["period"],
                            series=series,
                            value=value,
                            source_id=source["id"],
                        )
                    )
        for item in snapshot["evidence"]:
            db.merge(
                Evidence(id=item["id"], source_id=source["id"], metadata_json=item)
            )


if __name__ == "__main__":
    seed()
    print(
        "Published reviewed snapshot: 1 source, 52 observations, 3 evidence summaries"
    )
