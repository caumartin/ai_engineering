# Pipeline de Extracción de Entidades Técnicas

Sistema basado en **LangChain LCEL** + **Pydantic** que recibe texto no estructurado (descripciones de arquitectura, logs de error, etc.) y devuelve un objeto validado con:

- Lista de tecnologías identificadas
- Nivel de criticidad (`baja` | `media` | `alta`)
- Resumen técnico conciso


## Instalación

```bash
python -m venv env
source env/bin/activate   # Windows: env\Scripts\activate
pip install -r requirements.txt


## Para correr prueba ##

python test.py
