import json
from typing import Dict, Any, List
import httpx
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.mock_fallback = MockLLMProvider()

    async def generate_chat_response(
        self,
        system_prompt: str,
        chat_history: List[Dict[str, str]],
        user_message: str,
        student_context: Dict[str, Any]
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": system_prompt}]
        for h in chat_history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(
                    url,
                    headers=headers,
                    json={"model": self.model, "messages": messages, "temperature": 0.5}
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
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
        # Always use robust algorithm / fallback
        return await self.mock_fallback.generate_study_plan_items(free_slots, tasks, exams, options)
