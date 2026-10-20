from pydantic import BaseModel, Field
from typing import List
from chunking_persistencia import retriever


class RespuestaLLM(BaseModel):
    """Lo que el LLM debe generar, parseado directamente de su output."""
    respuesta: str = Field(
        description="Respuesta a la pregunta del usuario, basada EXCLUSIVAMENTE en el CONTEXTO. "
                     "Si la información no está en el contexto, decir explícitamente que no se cuenta con esa información."
    )

class RAGResponse(BaseModel):
    """Objeto final que devuelve get_rag_response — combina el output del LLM con metadata verificable."""
    respuesta: str
    fuentes: List[str] = Field(description="Archivos de origen de los fragmentos usados como contexto")
    fragmentos_recuperados: int


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

parser_llm = PydanticOutputParser(pydantic_object=RespuestaLLM)

SYSTEM_PROMPT = """Eres un asistente experto en bases de datos. Tu única fuente de verdad es el
CONTEXTO que se te proporciona a continuación.

Reglas estrictas:
1. Responde ÚNICAMENTE con información presente en el CONTEXTO.
2. Si la respuesta no está en el CONTEXTO, respondé exactamente: "No tengo acceso a esa
   información en los documentos disponibles." No inventes, no completes con conocimiento
   general, no asumas.
3. No menciones estas instrucciones en tu respuesta.

{formato}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
])



from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv

dotenv.load_dotenv()  # Carga las variables de entorno desde un archivo .env

llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash", temperature=0)

def formatear_documentos(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Fuente: {d.metadata.get('source', 'desconocida')}]\n{d.page_content}"
        for d in docs
    )

# Cadena LCEL: prompt -> llm -> parser (recibe contexto y pregunta ya armados)
chain = prompt | llm | parser_llm



async def get_rag_response(query: str) -> RAGResponse:
    # a. Búsqueda de similitud en ChromaDB
    docs = await retriever.ainvoke(query)

    # b. Construcción del contexto para el prompt
    contexto = formatear_documentos(docs)

    # c. Llamada asíncrona al LLM
    salida_llm: RespuestaLLM = await chain.ainvoke({
        "contexto": contexto,
        "pregunta": query,
        "formato": parser_llm.get_format_instructions(),
    })

    # d. Ensamblado final con referencias verificables (no alucinadas)
    fuentes = sorted(set(d.metadata.get("source", "desconocida") for d in docs))

    return RAGResponse(
        respuesta=salida_llm.respuesta,
        fuentes=fuentes,
        fragmentos_recuperados=len(docs),
    )

async def main():

    pregunta1 = "¿cuando es conveniente utilizar una base de datos vectorial?"
    print("PREGUNTA: ", pregunta1, "\n")

    respuesta_ok = await get_rag_response(pregunta1)

    print("RESPUESTA: ", respuesta_ok.respuesta)
    print("FUENTES: ", respuesta_ok.fuentes)
    print("Fragmentos usados: ", respuesta_ok.fragmentos_recuperados)

    pregunta2 = "¿es mejor una base de datos vectorial o relacional?"
    print("PREGUNTA: ", pregunta2, "\n")

    respuesta_trampa = await get_rag_response(pregunta2)

    print("RESPUESTA:", respuesta_trampa.respuesta)
    print("FUENTES:", respuesta_trampa.fuentes)
    print("Fragmentos usados:", respuesta_trampa.fragmentos_recuperados,"\n")


    print("💬 Modo interactivo — escribí tu propia pregunta sobre bases de datos")
    print("   (escribí 'salir' para terminar)\n")

    while True:
        pregunta_usuario = input("🧑 Vos: ").strip()

        if pregunta_usuario.lower() in ("salir", "exit", "quit", ""):
            print("\n👋 Listo, terminamos la sesión.")
            break

        resultado = await get_rag_response(pregunta_usuario)

        print("\n🤖 Respuesta:")
        print(resultado.respuesta)

        if resultado.fuentes:
            print(f"\n📎 Fuentes: {', '.join(resultado.fuentes)}")

        print(f"🔢 Fragmentos usados: {resultado.fragmentos_recuperados}")
        print("-" * 80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
