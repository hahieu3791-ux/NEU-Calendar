from typing import Dict, Any, List
import httpx
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model or "gemini-1.5-flash"
        self.mock_fallback = MockLLMProvider()

    async def generate_chat_response(
        self,
        system_prompt: str,
        chat_history: List[Dict[str, str]],
        user_message: str,
        student_context: Dict[str, Any]
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        for h in chat_history[-6:]:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.4}
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception:
            pass
        return await self.mock_fallback.generate_chat_response(system_prompt, chat_history, user_message, student_context)

    async def generate_study_plan_items(
        self,
        free_slots: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        exams: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        return await self.mock_fallback.generate_study_plan_items(free_slots, tasks, exams, options)
