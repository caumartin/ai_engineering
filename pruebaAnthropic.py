import os
import dotenv
import asyncio
from pydantic import SecretStr
from src.schemas import LLMConfig, Provider, ChatMessage, ModelResponse
from src.AsyncLLMManager import AsyncLLMManager

dotenv.load_dotenv()

async def main():

    config_anthropic = LLMConfig(
        provider=Provider.ANTHROPIC,
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=SecretStr(os.environ["ANTHROPIC_API_KEY"]),
        temperature=0.7,
        max_tokens=200,
    )

    manager_anthropic = AsyncLLMManager(config_anthropic)

    pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]

    resultado = await manager_anthropic.generate(pregunta)
    print("🟣 Anthropic:", resultado.content if not resultado.error else f"❌ {resultado.error}")

if __name__ == "__main__":
    asyncio.run(main())