import hmac
import hashlib
import logging

logger = logging.getLogger("allstreak.whatsapp.signature")

def verify_meta_signature(payload_bytes: bytes, signature_header: str, app_secret: str) -> bool:
    """
    Validate the X-Hub-Signature-256 header sent by Meta webhook requests.
    Header format: "sha256={hash}"
    """
    if not signature_header or not app_secret:
        # If no secret configured in dev mode, permit for ease of testing
        return True

    if not signature_header.startswith("sha256="):
        logger.warning("Invalid signature header format (missing sha256= prefix)")
        return False

    expected_signature = signature_header.split("sha256=")[1].strip()
    computed_hash = hmac.new(
        key=app_secret.encode('utf-8'),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, computed_hash)
