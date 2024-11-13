# guardrails_manager.py
import os
from nemoguardrails import LLMRails, RailsConfig
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class GuardrailsWrapper(LLM):
    """Wrapper for integrating LangChain LLM with NeMo Guardrails."""

    llm: Any = Field(...)
    llm_rails: Any = None

    class Config:
        # Adjust Config for Pydantic v2
        arbitrary_types_allowed = True
        extra = "allow"

    def __init__(self, llm, config_path="guardrails/saathi_guardrails.yaml"):
        super().__init__()
        # Initialize LangChain LLM
        self.llm = llm
        # Load guardrails configuration
        config = RailsConfig.from_path(config_path)
        self.llm_rails = LLMRails(config=config)

    @property
    def _llm_type(self) -> str:
        return "guardrails_wrapper"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.llm_rails.generate(prompt)
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name": "GuardrailsWrapper"}
