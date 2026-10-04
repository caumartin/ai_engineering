import asyncio
import os
from pydantic import SecretStr
from src.schemas import LLMConfig, Provider, ChatMessage, ModelResponse
from src.AsyncLLMManager import AsyncLLMManager
import dotenv

dotenv.load_dotenv()

async def main():

    config_gemini = LLMConfig(
        provider=Provider.GEMINI,
        model="gemini-flash-latest",  # mismo alias estable que usamos en el proyecto RAG
        google_api_key=SecretStr(os.environ["GOOGLE_API_KEY"]),
        temperature=0.7,
        max_tokens=200,
    )

    manager_gemini = AsyncLLMManager(config_gemini)

    pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]

    resultado =  await manager_gemini.generate(pregunta)
    print("🔵 Gemini:", resultado.content if not resultado.error else f"❌ {resultado.error}")

    print("\n🔵 Streaming Gemini:")
    async for chunk in manager_gemini.generate_stream(pregunta):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())