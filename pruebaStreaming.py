import asyncio
import os
import dotenv
from src.schemas import LLMConfig, Provider, ChatMessage
from src.AsyncLLMManager import AsyncLLMManager
from pydantic import SecretStr

dotenv.load_dotenv()

config_openai = LLMConfig(
    provider=Provider.OPENAI,
    model="gpt-4o-mini",
    openai_api_key=SecretStr(os.environ["OPENAI_API_KEY"]),
    temperature=0.7,
    max_tokens=200,
)

config_anthropic = LLMConfig(
    provider=Provider.ANTHROPIC,
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=SecretStr(os.environ["ANTHROPIC_API_KEY"]),
    temperature=0.7,
    max_tokens=200,
)

manager_openai = AsyncLLMManager(config_openai)
manager_anthropic = AsyncLLMManager(config_anthropic)

pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]

async def main():

    print("🟢 Streaming OpenAI:")
    async for chunk in manager_openai.generate_stream(pregunta):
        print(chunk, end="", flush=True)

    print("\n\n🟣 Streaming Anthropic:")
    async for chunk in manager_anthropic.generate_stream(pregunta):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
