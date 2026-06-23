"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str = Field(..., description="Agent name")
    description: str = Field(default="", description="Agent description")
    model: str = Field(default="default", description="LLM model to use")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class AgentResult(BaseModel):
    """Result from an agent."""

    agent_name: str = Field(..., description="Agent name")
    success: bool = Field(default=True, description="Whether the operation succeeded")
    output: Any = Field(default=None, description="Agent output")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Result metadata")


class BaseAgent(ABC):
    """Base class for all specialized agents."""

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig(name=self.__class__.__name__)

    @abstractmethod
    def process(self, input_data: Any) -> AgentResult:
        """Process input data and return result.

        Args:
            input_data: Input data to process

        Returns:
            Agent result
        """
        pass

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid
        """
        return input_data is not None

    def log(self, message: str) -> None:
        """Log a message.

        Args:
            message: Message to log
        """
        print(f"[{self.config.name}] {message}")