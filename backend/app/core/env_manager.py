import os
import re
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("allstreak.env_manager")

# Resolve project root: .../Allstreak/backend/app/core/env_manager.py -> .../Allstreak
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"

def get_env_path() -> Path:
    return ENV_PATH

def sync_env_file(updates: Dict[str, str]) -> Dict[str, str]:
    """
    Updates or appends key-value pairs in the project's .env file.
    Also updates os.environ and the active in-memory settings.
    """
    # 1. If .env does not exist, initialize it from .env.example or create new
    if not ENV_PATH.exists():
        if ENV_EXAMPLE_PATH.exists():
            try:
                content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
                ENV_PATH.write_text(content, encoding="utf-8")
                logger.info(f"Initialized .env from .env.example at {ENV_PATH}")
            except Exception as e:
                logger.warning(f"Could not copy .env.example: {e}")
                ENV_PATH.write_text("", encoding="utf-8")
        else:
            ENV_PATH.write_text("", encoding="utf-8")

    # 2. Read existing .env lines
    try:
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        logger.error(f"Failed to read .env file: {e}")
        lines = []

    remaining_updates = dict(updates)
    new_lines = []

    # 3. Update existing keys in-place to preserve comments and formatting
    for line in lines:
        stripped = line.strip()
        # Check if this line is an assignment: KEY=VALUE
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in remaining_updates:
                val = remaining_updates.pop(key)
                new_lines.append(f"{key}={val}")
                continue
        new_lines.append(line)

    # 4. If any keys were not found in the file, append them
    if remaining_updates:
        if new_lines and new_lines[-1].strip() != "":
            new_lines.append("")
        new_lines.append("# Meta WhatsApp Cloud API (Automated Sync)")
        for key, val in remaining_updates.items():
            new_lines.append(f"{key}={val}")

    # 5. Write back to .env
    try:
        ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        logger.info(f"Successfully updated .env at {ENV_PATH} with {list(updates.keys())}")
    except Exception as e:
        logger.error(f"Failed to write to .env file: {e}")
        raise RuntimeError(f"Could not write to .env file: {e}")

    # 6. Synchronize in-memory os.environ & settings
    for key, val in updates.items():
        os.environ[key] = str(val)

    try:
        from backend.app.config import settings
        for key, val in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, val)
    except Exception as e:
        logger.warning(f"Could not update in-memory settings: {e}")

    return updates


def read_meta_from_env() -> Dict[str, Optional[str]]:
    """
    Reads the current Meta Cloud API values from .env or os.environ / settings.
    """
    from backend.app.config import settings

    return {
        "access_token": os.getenv("META_ACCESS_TOKEN") or getattr(settings, "META_ACCESS_TOKEN", "") or "",
        "phone_number_id": os.getenv("META_PHONE_NUMBER_ID") or getattr(settings, "META_PHONE_NUMBER_ID", "") or "",
        "waba_id": os.getenv("META_WABA_ID") or getattr(settings, "META_WABA_ID", "") or "",
        "webhook_verify_token": os.getenv("META_VERIFY_TOKEN") or getattr(settings, "META_VERIFY_TOKEN", "") or "allstreak_secure_verify_token_2026",
        "business_id": os.getenv("META_BUSINESS_ID") or getattr(settings, "META_BUSINESS_ID", "") or "",
        "app_secret": os.getenv("META_APP_SECRET") or getattr(settings, "META_APP_SECRET", "") or "",
    }
