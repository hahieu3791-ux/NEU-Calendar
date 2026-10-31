from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_chat_response(
        self,
        system_prompt: str,
        chat_history: List[Dict[str, str]],
        user_message: str,
        student_context: Dict[str, Any]
    ) -> str:
        """Generate response for academic chat assistant."""
        pass

    @abstractmethod
    async def generate_study_plan_items(
        self,
        free_slots: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        exams: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate study plan distribution."""
        pass
