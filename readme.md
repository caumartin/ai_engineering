# AI Engineering #

## Pre entrega 1 (commit v1.1) ##

### Cliente LLM asincrono ###

** Para correr: **

definir api keys en archivo .env

pip install -r requirements.txt

python main.py

** Correcciones en v1.1: **

- se cambio modelo gemini a 3.5-flash para evitar error por alta demanda.
- se dejó de enviar temperatura a modelo Anthropic evitar error de parámetro no esperado.
