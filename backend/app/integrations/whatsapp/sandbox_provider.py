import uuid
import logging
from typing import Dict, Any, List, Optional
from backend.app.integrations.whatsapp.provider import WhatsAppProvider, SendMessageResult

logger = logging.getLogger("allstreak.whatsapp.sandbox")

class SandboxWhatsAppProvider(WhatsAppProvider):
    """Sandbox simulator provider for zero-config testing and interactive playground."""

    def __init__(self, phone_number_id: str = "sandbox_phone_12345"):
        self.phone_number_id = phone_number_id

    def _generate_fake_wamid(self) -> str:
        return f"wamid.HBg{uuid.uuid4().hex[:16]}="

    async def send_text(
        self,
        to_phone: str,
        text: str,
        preview_url: bool = False,
        buttons: Optional[List[str]] = None
    ) -> SendMessageResult:
        meta_id = self._generate_fake_wamid()
        logger.info(f"[SANDBOX OUTGOING] To: {to_phone} | Message: {text} | Buttons: {buttons} | ID: {meta_id}")
        return SendMessageResult(
            success=True,
            meta_message_id=meta_id,
            raw_response={"messaging_product": "whatsapp", "messages": [{"id": meta_id}], "mode": "sandbox"}
        )

    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> SendMessageResult:
        meta_id = self._generate_fake_wamid()
        logger.info(f"[SANDBOX TEMPLATE] To: {to_phone} | Template: {template_name} ({language_code}) | ID: {meta_id}")
        return SendMessageResult(
            success=True,
            meta_message_id=meta_id,
            raw_response={"messaging_product": "whatsapp", "messages": [{"id": meta_id}], "template": template_name, "mode": "sandbox"}
        )

    async def send_media(
        self,
        to_phone: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> SendMessageResult:
        meta_id = self._generate_fake_wamid()
        logger.info(f"[SANDBOX MEDIA] To: {to_phone} | Type: {media_type} | URL: {media_url} | ID: {meta_id}")
        return SendMessageResult(
            success=True,
            meta_message_id=meta_id,
            raw_response={"messaging_product": "whatsapp", "messages": [{"id": meta_id}], "mode": "sandbox"}
        )

    async def send_location(
        self,
        to_phone: str,
        latitude: float,
        longitude: float,
        name: str,
        address: str
    ) -> SendMessageResult:
        meta_id = self._generate_fake_wamid()
        logger.info(f"[SANDBOX LOCATION] To: {to_phone} | Lat: {latitude}, Lng: {longitude} | ID: {meta_id}")
        return SendMessageResult(
            success=True,
            meta_message_id=meta_id,
            raw_response={"messaging_product": "whatsapp", "messages": [{"id": meta_id}], "mode": "sandbox"}
        )

    async def validate_credentials(self) -> Dict[str, Any]:
        return {
            "valid": True,
            "display_phone_number": "+1 (555) 019-2834",
            "verified_name": "ALLSTREAK Sandbox Demo",
            "quality_rating": "GREEN",
        }

    async def fetch_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "tpl_sandbox_001",
                "name": "welcome_greeting",
                "status": "APPROVED",
                "category": "UTILITY",
                "language": "en_US",
                "components": [
                    {"type": "BODY", "text": "Hello {{1}}, welcome to ALLSTREAK! How can we assist you today?"},
                    {"type": "FOOTER", "text": "Reply STOP to unsubscribe"}
                ]
            },
            {
                "id": "tpl_sandbox_002",
                "name": "order_update",
                "status": "APPROVED",
                "category": "UTILITY",
                "language": "en_US",
                "components": [
                    {"type": "BODY", "text": "Hello {{1}}, your order #{{2}} has been confirmed and is being processed."}
                ]
            }
        ]
