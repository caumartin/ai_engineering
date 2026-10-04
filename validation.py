from src.schemas import LLMConfig, Provider
from pydantic import ValidationError

try:
    LLMConfig(provider=Provider.OPENAI, model="gpt-4o-mini", temperature=5)
except ValidationError as e:
    print("❌ Se detectó ANTES de llamar a la API:\n", e)