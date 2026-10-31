from typing import Dict, Any, List
import httpx
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model or "claude-3-haiku-20240307"
        self.mock_fallback = MockLLMProvider()

    async def generate_chat_response(
        self,
        system_prompt: str,
        chat_history: List[Dict[str, str]],
        user_message: str,
        student_context: Dict[str, Any]
    ) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        messages = []
        for h in chat_history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(
                    url,
                    headers=headers,
                    json={
                        "model": self.model,
                        "system": system_prompt,
                        "messages": messages,
                        "max_tokens": 800,
                        "temperature": 0.5
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("content", [])
                    if content and "text" in content[0]:
                        return content[0]["text"]
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
