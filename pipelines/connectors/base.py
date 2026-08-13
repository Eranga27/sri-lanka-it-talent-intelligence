from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseConnector(ABC):
    def __init__(self, source_id: str, config: Dict[str, Any] = None):
        self.source_id = source_id
        self.config = config or {}

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def validate(self, raw_data: List[Dict[str, Any]]) -> bool:
        """Validate raw data against expected schema."""
        pass

    @abstractmethod
    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize raw data into canonical format."""
        pass

    @abstractmethod
    def persist(self, normalized_data: List[Dict[str, Any]]) -> None:
        """Persist normalized data into the target layer."""
        pass
