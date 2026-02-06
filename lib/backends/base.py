"""Abstract base class for memory backends."""
from abc import ABC, abstractmethod
from typing import List

from ..models import Memory, Relationship, KnowledgeGraph, OperationInfo


class Backend(ABC):
    """Abstract interface that all backends must implement."""

    @abstractmethod
    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        """Search for memories by semantic similarity."""
        pass

    @abstractmethod
    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        """Search for relationships between entities."""
        pass

    @abstractmethod
    def save(self, content: str, group_id: str, **metadata) -> str:
        """Save new memory/episode."""
        pass

    @abstractmethod
    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        """Deep traversal from a starting memory."""
        pass

    @abstractmethod
    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        """List recent memories."""
        pass

    # Dynamic discovery methods

    @abstractmethod
    def get_capabilities(self) -> List[OperationInfo]:
        """Discover available operations for this backend."""
        pass

    @abstractmethod
    def get_schema(self, operation: str) -> dict:
        """Get parameter schema for an operation."""
        pass

    @abstractmethod
    def get_examples(self, operation: str) -> List[str]:
        """Get usage examples for an operation."""
        pass
