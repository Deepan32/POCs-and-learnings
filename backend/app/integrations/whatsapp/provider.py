from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class SendMessageResult(BaseModel):
    success: bool
    meta_message_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class WhatsAppProvider(ABC):
    """Abstract Base Class for WhatsApp Business API Providers."""

    @abstractmethod
    async def send_text(
        self,
        to_phone: str,
        text: str,
        preview_url: bool = False,
        buttons: Optional[List[str]] = None
    ) -> SendMessageResult:
        """Send a free-form text or interactive button message."""
        pass

    @abstractmethod
    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language_code: str,
        components: Optional[List[Dict[str, Any]]] = None
    ) -> SendMessageResult:
        """Send an approved WhatsApp message template."""
        pass

    @abstractmethod
    async def send_media(
        self,
        to_phone: str,
        media_type: str,  # image, video, audio, document
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> SendMessageResult:
        """Send media file."""
        pass

    @abstractmethod
    async def send_location(
        self,
        to_phone: str,
        latitude: float,
        longitude: float,
        name: str,
        address: str
    ) -> SendMessageResult:
        """Send geographic location."""
        pass

    @abstractmethod
    async def validate_credentials(self) -> Dict[str, Any]:
        """Validate account credentials with provider API."""
        pass

    @abstractmethod
    async def fetch_templates(self) -> List[Dict[str, Any]]:
        """Fetch all WhatsApp message templates from provider."""
        pass
