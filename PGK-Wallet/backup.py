#!/usr/bin/env python3
"""
PGK Wallet - backup utility.

Creates a timestamped .zip archive containing the SQLite database file and
all uploaded payment receipts. Run manually or via cron:

    python backup.py                # backup into ./backups/
    python backup.py --out /path    # backup into a custom directory
"""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def find_sqlite_path(database_url: str) -> Path | None:
    if not database_url.startswith("sqlite"):
        return None
    # sqlite:///./data/pgk_wallet.db  ->  ./data/pgk_wallet.db
    raw_path = database_url.split("sqlite:///", 1)[-1]
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup PGK Wallet's database and receipts.")
    parser.add_argument("--out", default=str(BASE_DIR / "backups"), help="Output directory for the backup archive.")
    args = parser.parse_args()

    try:
        from config import get_settings
        settings = get_settings()
        database_url = settings.database_url
    except Exception as exc:
        print(f"Could not load configuration ({exc}); falling back to default DB path.", file=sys.stderr)
        database_url = "sqlite:///./data/pgk_wallet.db"

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = out_dir / f"pgk_wallet_backup_{timestamp}.zip"

    db_path = find_sqlite_path(database_url)
    receipts_dir = BASE_DIR / "receipts"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if db_path and db_path.exists():
            zf.write(db_path, arcname=f"data/{db_path.name}")
        else:
            print("Warning: SQLite database file not found; skipping.", file=sys.stderr)

        if receipts_dir.exists():
            for file_path in receipts_dir.rglob("*"):
                if file_path.is_file():
                    zf.write(file_path, arcname=f"receipts/{file_path.relative_to(receipts_dir)}")

    print(f"Backup created: {archive_path}")


if __name__ == "__main__":
    main()
