"""Graphiti backend implementation."""
from datetime import datetime
from typing import List

from ..models import Memory, Relationship, KnowledgeGraph, OperationInfo
from .base import Backend


class GraphitiBackend(Backend):
    """Backend implementation for Graphiti MCP server."""

    # Static operation definitions
    OPERATIONS = {
        "query": {
            "description": "Search for memories by semantic similarity",
            "params": {"query": "str", "limit": "int"},
            "example": 'memory.query("auth patterns", limit=10)'
        },
        "search_facts": {
            "description": "Search for relationships between entities",
            "params": {"query": "str", "limit": "int"},
            "example": 'memory.search_facts("authentication flow", limit=20)'
        },
        "save": {
            "description": "Save new episode to knowledge graph",
            "params": {"content": "str", "title": "str (optional)"},
            "example": 'memory.save("Decision: Using JWT for auth", title="Auth Decision")'
        },
        "explore": {
            "description": "Deep traversal from a starting memory",
            "params": {"starting_point": "str", "depth": "int"},
            "example": 'memory.explore("authentication", depth=2)'
        },
        "list_recent": {
            "description": "List recent memories",
            "params": {"limit": "int"},
            "example": 'memory.list_recent(limit=20)'
        }
    }

    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        """Search memories using Graphiti search_memory_nodes."""
        # NOTE: Actual MCP call will be added when integrating with commands
        # For now, this is a stub that returns the expected structure

        # Future implementation:
        # result = mcp__graphiti__search_memory_nodes({
        #     "query": query,
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_nodes_to_memories(result)

        return []

    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        """Search relationships using Graphiti search_memory_facts."""
        # Future implementation:
        # result = mcp__graphiti__search_memory_facts({
        #     "query": query,
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_facts_to_relationships(result)

        return []

    def save(self, content: str, group_id: str, **metadata) -> str:
        """Save episode using Graphiti add_memory."""
        # Future implementation:
        # result = mcp__graphiti__add_memory({
        #     "episode_body": content,
        #     "group_id": group_id,
        #     "name": metadata.get("title", "Untitled"),
        #     "source": "context-hub",
        # })
        # return result.get("episode_id", "")

        return "stub-episode-id"

    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        """Explore knowledge graph from starting point."""
        # Combine nodes + facts to build graph
        nodes = self.query(starting_point, group_id, 10)
        edges = self.search_facts(starting_point, group_id, 20)

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        """List recent episodes using get_episodes."""
        # Future implementation:
        # result = mcp__graphiti__get_episodes({
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_episodes_to_memories(result)

        return []

    # Dynamic discovery

    def get_capabilities(self) -> List[OperationInfo]:
        """Return available operations."""
        return [
            OperationInfo(name=op, **details)
            for op, details in self.OPERATIONS.items()
        ]

    def get_schema(self, operation: str) -> dict:
        """Get schema for operation."""
        if operation not in self.OPERATIONS:
            raise ValueError(f"Unknown operation: {operation}")

        op_info = self.OPERATIONS[operation]
        return {
            "description": op_info["description"],
            "params": op_info["params"]
        }

    def get_examples(self, operation: str) -> List[str]:
        """Get usage examples."""
        if operation not in self.OPERATIONS:
            raise ValueError(f"Unknown operation: {operation}")

        return [self.OPERATIONS[operation]["example"]]

    # Helper methods (future implementation)

    def _parse_nodes_to_memories(self, result: dict) -> List[Memory]:
        """Parse Graphiti nodes to Memory objects."""
        memories = []

        for node in result.get("nodes", []):
            memories.append(Memory(
                id=node.get("uuid", ""),
                content=node.get("name", ""),
                created_at=datetime.fromisoformat(node.get("created_at", datetime.now().isoformat())),
                metadata={"summary": node.get("summary", "")}
            ))

        return memories

    def _parse_facts_to_relationships(self, result: dict) -> List[Relationship]:
        """Parse Graphiti facts to Relationship objects."""
        relationships = []

        for fact in result.get("facts", []):
            relationships.append(Relationship(
                source=fact.get("source_node_uuid", ""),
                target=fact.get("target_node_uuid", ""),
                relation_type=fact.get("fact", ""),
                metadata={"created_at": fact.get("created_at", "")}
            ))

        return relationships
