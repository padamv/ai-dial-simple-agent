from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        pass

    def _inline_schema_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Inline $defs/$ref for tool parameter schemas (keeps OpenAI-compatible JSON Schema)."""
        defs = schema.get("$defs", {})

        def resolve(node: Any) -> Any:
            if isinstance(node, dict):
                ref = node.get("$ref")
                if ref and ref.startswith("#/$defs/"):
                    key = ref.split("/")[-1]
                    return resolve(defs.get(key, {}))
                return {key: resolve(value) for key, value in node.items() if key != "$defs"}
            if isinstance(node, list):
                return [resolve(item) for item in node]
            return node

        return resolve(schema)

    @property
    def schema(self) -> dict[str, Any]:
        """Provides tools JSON Schema"""
        parameters = self._inline_schema_refs(self.input_schema)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters
            }
        }