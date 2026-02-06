"""Main memory adapter that routes to backends."""
from typing import List

from .backends import Backend, GraphitiBackend, ForgetfulBackend
from .config import Config, load_config, detect_group_id
from .models import Memory, Relationship, KnowledgeGraph, OperationInfo


class MemoryAdapter:
    """
    Unified interface for memory operations.

    Automatically detects backend from config and routes operations
    to appropriate implementation (Graphiti or Forgetful).
    """

    def __init__(self, config: Config = None):
        """
        Initialize adapter with config.

        Args:
            config: Configuration (loads from file if None)
        """
        self.config = config or load_config()
        self.group_id = detect_group_id(self.config)
        self.backend = self._create_backend()

    def _create_backend(self) -> Backend:
        """Create backend instance based on config."""
        backend_name = self.config.memory.backend.lower()

        if backend_name == "graphiti":
            return GraphitiBackend()
        elif backend_name == "forgetful":
            return ForgetfulBackend()
        else:
            raise ValueError(f"Unknown backend: {backend_name}")

    # Core operations (delegate to backend)

    def query(self, query: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories by semantic similarity.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching memories
        """
        return self.backend.query(query, self.group_id, limit)

    def search_facts(self, query: str, limit: int = 10) -> List[Relationship]:
        """
        Search for relationships between entities.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of relationships
        """
        return self.backend.search_facts(query, self.group_id, limit)

    def save(self, content: str, **metadata) -> str:
        """
        Save new memory/episode.

        Args:
            content: Memory content
            **metadata: Backend-specific metadata (title, importance, etc.)

        Returns:
            Memory/episode ID
        """
        return self.backend.save(content, self.group_id, **metadata)

    def explore(self, starting_point: str, depth: int = 2) -> KnowledgeGraph:
        """
        Deep traversal from a starting memory.

        Args:
            starting_point: Query to find starting memories
            depth: How many levels to traverse

        Returns:
            Knowledge graph of connected memories
        """
        return self.backend.explore(starting_point, self.group_id, depth)

    def list_recent(self, limit: int = 20) -> List[Memory]:
        """
        List recent memories.

        Args:
            limit: Maximum results

        Returns:
            List of recent memories
        """
        return self.backend.list_recent(self.group_id, limit)

    # Dynamic discovery

    def list_operations(self) -> List[OperationInfo]:
        """
        Discover available operations for current backend.

        Returns:
            List of operation info
        """
        return self.backend.get_capabilities()

    def get_operation_schema(self, operation: str) -> dict:
        """
        Get parameter schema for an operation.

        Args:
            operation: Operation name

        Returns:
            Schema dictionary
        """
        return self.backend.get_schema(operation)

    def get_operation_examples(self, operation: str) -> List[str]:
        """
        Get usage examples for an operation.

        Args:
            operation: Operation name

        Returns:
            List of example code strings
        """
        return self.backend.get_examples(operation)
