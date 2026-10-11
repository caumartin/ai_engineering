from enum import Enum
from typing import List
from pydantic import BaseModel, Field, constr


class NivelCriticidad(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class TechnicalEntitySchema(BaseModel):
    tecnologias: List[str] = Field(
        ...,
        description="Lista de tecnologías, frameworks, bases de datos o servicios cloud identificados en el texto.",
        min_items=1
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        ...,
        description="Nivel de criticidad o severidad del problema, incidente o arquitectura descrita."
    )
    resumen_tecnico: str = Field(
        ...,
        description="Breve resumen técnico que condense la arquitectura, problema o estado del sistema en una sola oración concisa."
    )


class PipelineInput(BaseModel):
    input_text: str = Field(
        ...,
        min_length=10,
        description="El texto de entrada crudo que debe ser analizado, con un mínimo de longitud."
    )
