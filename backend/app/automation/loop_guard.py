import logging
from backend.app.models.message import Message, MessageDirection, MessageOrigin

logger = logging.getLogger("allstreak.automation.loop_guard")

class LoopGuard:
    MAX_DEPTH: int = 5

    @staticmethod
    def is_loop_safe(incoming_message: Message, current_depth: int = 0) -> bool:
        """
        Check if message should trigger automation:
        - Must be INBOUND (customer message). Never reply to OUTBOUND messages.
        - Origin must be CUSTOMER.
        - Execution depth must be less than MAX_DEPTH.
        """
        if incoming_message.direction != MessageDirection.INBOUND:
            logger.warning(f"LoopGuard prevented trigger: message {incoming_message.id} is {incoming_message.direction}")
            return False

        if incoming_message.origin != MessageOrigin.CUSTOMER:
            logger.warning(f"LoopGuard prevented trigger: origin is {incoming_message.origin}")
            return False

        if current_depth >= LoopGuard.MAX_DEPTH:
            logger.warning(f"LoopGuard prevented trigger: execution depth {current_depth} exceeded limit")
            return False

        return True
