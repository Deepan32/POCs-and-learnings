import logging
from typing import Dict, Any, List, Optional
import httpx
from backend.app.integrations.whatsapp.provider import WhatsAppProvider, SendMessageResult

logger = logging.getLogger("allstreak.whatsapp.meta")

class MetaWhatsAppProvider(WhatsAppProvider):
    """Production Meta WhatsApp Cloud API Provider."""

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        waba_id: Optional[str] = None,
        graph_url: str = "https://graph.facebook.com",
        api_version: str = "v21.0"
    ):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.waba_id = waba_id
        self.base_url = f"{graph_url}/{api_version}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _clean_phone(self, phone: str) -> str:
        # Strip '+' and any spaces/dashes
        return "".join(c for c in phone if c.isdigit())

    async def send_text(
        self,
        to_phone: str,
        text: str,
        preview_url: bool = False,
        buttons: Optional[List[str]] = None
    ) -> SendMessageResult:
        clean_phone = self._clean_phone(to_phone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        # If interactive buttons provided (up to 3 for WhatsApp interactive button format)
        if buttons and len(buttons) > 0:
            formatted_buttons = []
            for idx, btn_title in enumerate(buttons[:3]):
                formatted_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{idx}_{btn_title.lower().replace(' ', '_')}",
                        "title": btn_title[:20]  # Meta limit is 20 chars
                    }
                })
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text},
                    "action": {"buttons": formatted_buttons}
                }
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": text
                }
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                data = response.json()
                if response.status_code in [200, 201] and "messages" in data:
                    meta_id = data["messages"][0]["id"]
                    return SendMessageResult(success=True, meta_message_id=meta_id, raw_response=data)
                else:
                    err_msg = data.get("error", {}).get("message", response.text)
                    logger.error(f"Meta send_text failed: {err_msg}")
                    return SendMessageResult(success=False, error_message=err_msg, raw_response=data)
        except Exception as e:
            logger.exception(f"Exception calling Meta API send_text: {e}")
            return SendMessageResult(success=False, error_message=str(e))

    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> SendMessageResult:
        clean_phone = self._clean_phone(to_phone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                data = response.json()
                if response.status_code in [200, 201] and "messages" in data:
                    meta_id = data["messages"][0]["id"]
                    return SendMessageResult(success=True, meta_message_id=meta_id, raw_response=data)
                else:
                    err_msg = data.get("error", {}).get("message", response.text)
                    logger.error(f"Meta send_template failed: {err_msg}")
                    return SendMessageResult(success=False, error_message=err_msg, raw_response=data)
        except Exception as e:
            logger.exception(f"Exception calling Meta API send_template: {e}")
            return SendMessageResult(success=False, error_message=str(e))

    async def send_media(
        self,
        to_phone: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> SendMessageResult:
        clean_phone = self._clean_phone(to_phone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        media_payload: Dict[str, Any] = {"link": media_url}
        if caption and media_type in ["image", "video", "document"]:
            media_payload["caption"] = caption
        if filename and media_type == "document":
            media_payload["filename"] = filename

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": media_type,
            media_type: media_payload
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                data = response.json()
                if response.status_code in [200, 201] and "messages" in data:
                    return SendMessageResult(success=True, meta_message_id=data["messages"][0]["id"], raw_response=data)
                else:
                    return SendMessageResult(success=False, error_message=data.get("error", {}).get("message", response.text), raw_response=data)
        except Exception as e:
            return SendMessageResult(success=False, error_message=str(e))

    async def send_location(
        self,
        to_phone: str,
        latitude: float,
        longitude: float,
        name: str,
        address: str
    ) -> SendMessageResult:
        clean_phone = self._clean_phone(to_phone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                data = response.json()
                if response.status_code in [200, 201] and "messages" in data:
                    return SendMessageResult(success=True, meta_message_id=data["messages"][0]["id"], raw_response=data)
                else:
                    return SendMessageResult(success=False, error_message=data.get("error", {}).get("message", response.text), raw_response=data)
        except Exception as e:
            return SendMessageResult(success=False, error_message=str(e))

    async def validate_credentials(self) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.phone_number_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                data = response.json()
                if response.status_code == 200:
                    return {
                        "valid": True,
                        "display_phone_number": data.get("display_phone_number"),
                        "verified_name": data.get("verified_name"),
                        "quality_rating": data.get("quality_rating", "GREEN"),
                    }
                return {"valid": False, "error": data.get("error", {}).get("message", "Validation failed")}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def fetch_templates(self) -> List[Dict[str, Any]]:
        if not self.waba_id:
            return []
        url = f"{self.base_url}/{self.waba_id}/message_templates"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json().get("data", [])
                return []
        except Exception as e:
            logger.error(f"Failed to fetch templates from Meta: {e}")
            return []
