import asyncio
import dotenv
import os
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

    config_anthropic = LLMConfig(
        provider=Provider.ANTHROPIC,
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=SecretStr(os.environ["ANTHROPIC_API_KEY"]),
        temperature=0.7,
        max_tokens=200,
    )

    config_gemini = LLMConfig(
        provider=Provider.GEMINI,
        model="gemini-3.5-flash",  # mismo alias estable que usamos en el proyecto RAG
        google_api_key=SecretStr(os.environ["GOOGLE_API_KEY"]),
        temperature=0.7,
        max_tokens=200,
    )

    manager_openai = AsyncLLMManager(config_openai)
    manager_anthropic = AsyncLLMManager(config_anthropic)
    manager_gemini = AsyncLLMManager(config_gemini)

    pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]

    print ("\n######## Comparación de resultados entre OpenAI, Anthropic y Gemini ##########")

    try:
        resultado = await manager_openai.generate(pregunta)
        print("\n\n🟢 OpenAI:", resultado.content if not resultado.error else f"❌ {resultado.error}")
    except Exception as e:
        print(f"❌ Error al generar respuesta con OpenAI: {e}")

    try:
        print("\n🔵 Streaming OpenAI:")
        async for chunk in manager_openai.generate_stream(pregunta):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"❌ Error al hacer streaming con OpenAI: {e}")   


    try:
        resultado = await manager_anthropic.generate(pregunta)
        print("\n\n🟢 Anthropic:", resultado.content if not resultado.error else f"❌ {resultado.error}")
    except Exception as e:
        print(f"❌ Error al generar respuesta con Anthropic: {e}")

    try:
        print("\n🔵 Streaming Anthropic:")
        async for chunk in manager_anthropic.generate_stream(pregunta):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"❌ Error al hacer streaming con Anthropic: {e}")


    try:
        resultado = await manager_gemini.generate(pregunta)
        print("\n\n🟢 Gemini:", resultado.content if not resultado.error else f"❌ {resultado.error}")
    except Exception as e:
        print(f"❌ Error al generar respuesta con Gemini: {e}")

    try:
        print("\n🔵 Streaming Gemini:")
        async for chunk in manager_gemini.generate_stream(pregunta):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"❌ Error al hacer streaming con Gemini: {e}")
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
