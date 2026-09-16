"""
PGK Wallet - entry point.

Run with: python main.py
Requires a valid .env file (see .env.example).
"""
from __future__ import annotations

import sys

from telegram.ext import Application

from config import LOG_DIR, get_settings
from app.bot.handler_registry import register_handlers
from app.bot.jobs import poll_pending_invoices
from app.database.database import init_db
from app.utils.logging_setup import setup_logging


def main() -> None:
    try:
        settings = get_settings()
    except Exception as exc:  # pragma: no cover - startup misconfiguration
        print(f"Configuration error: {exc}\nCopy .env.example to .env and fill in the required values.", file=sys.stderr)
        sys.exit(1)

    logger = setup_logging(LOG_DIR, settings.log_level)
    logger.info("Starting PGK Wallet...")

    init_db(settings.database_url)
    logger.info("Database initialized.")

    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings

    register_handlers(app)

    if app.job_queue is not None:
        app.job_queue.run_repeating(
            poll_pending_invoices,
            interval=settings.polling_interval_seconds,
            first=10,
            name="poll_pending_invoices",
        )
        logger.info(f"Payment polling job scheduled every {settings.polling_interval_seconds}s.")
    else:
        logger.warning(
            "JobQueue not available (install python-telegram-bot[job-queue]); "
            "automatic payment polling is disabled. Customers can still use 'I've Paid'."
        )

    logger.info("PGK Wallet is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
