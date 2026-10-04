import os
import dotenv
import asyncio
from pydantic import SecretStr
from src.schemas import LLMConfig, Provider, ChatMessage, ModelResponse
from src.AsyncLLMManager import AsyncLLMManager

dotenv.load_dotenv()

async def main():

    config_openai = LLMConfig(
        provider=Provider.OPENAI,
        model="gpt-4o-mini",
        openai_api_key=SecretStr(os.environ["OPENAI_API_KEY"]),
        temperature=0.7,
        max_tokens=200,
    )

    manager_openai = AsyncLLMManager(config_openai)

    pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]

    resultado = await manager_openai.generate(pregunta)
    print("🟢 OpenAI:", resultado.content if not resultado.error else f"❌ {resultado.error}")

if __name__ == "__main__":
    asyncio.run(main())