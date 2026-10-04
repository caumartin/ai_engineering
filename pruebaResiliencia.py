import asyncio
from pydantic import SecretStr
from src.schemas import LLMConfig, Provider, ChatMessage, ModelResponse
from src.AsyncLLMManager import AsyncLLMManager

async def main():

    config_rota = LLMConfig(
        provider=Provider.OPENAI,
        model="gpt-4o-mini",
        openai_api_key=SecretStr("sk-key-invalida-a-proposito"),
    )

    manager_roto = AsyncLLMManager(config_rota)
    pregunta = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas.")]
    resultado = await manager_roto.generate(pregunta)

    print("¿El programa siguió vivo?: ✅ Sí")
    print("Error capturado (sin crash):", resultado.error)

if __name__ == "__main__":
    asyncio.run(main())
