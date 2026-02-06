"""
Bridge module for Claude Code commands to access memory adapter.

Commands are markdown files that Claude interprets. This module provides
simple functions that can be called from command context.
"""
import sys
from pathlib import Path

# Add parent directory to path for package import
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from lib.memory_adapter import MemoryAdapter
from lib.models import Memory, Relationship, KnowledgeGraph


# Global adapter instance (initialized on first use)
_adapter = None


def get_adapter() -> MemoryAdapter:
    """Get or create the global adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = MemoryAdapter()
    return _adapter


# Simple wrapper functions that Claude can call

def memory_query(query: str, limit: int = 10) -> list:
    """
    Search for memories.

    Args:
        query: Search query text
        limit: Maximum results

    Returns:
        List of memory dictionaries
    """
    adapter = get_adapter()
    memories = adapter.query(query, limit)

    # Convert to simple dicts for easy consumption
    return [
        {
            'id': m.id,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'importance': m.importance,
            'metadata': m.metadata
        }
        for m in memories
    ]


def memory_save(content: str, **metadata) -> str:
    """
    Save a new memory.

    Args:
        content: Memory content
        **metadata: title, importance, keywords, tags, etc.

    Returns:
        Memory ID
    """
    adapter = get_adapter()
    return adapter.save(content, **metadata)


def memory_list_recent(limit: int = 20) -> list:
    """List recent memories."""
    adapter = get_adapter()
    memories = adapter.list_recent(limit)

    return [
        {
            'id': m.id,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'importance': m.importance,
            'metadata': m.metadata
        }
        for m in memories
    ]


def memory_explore(starting_point: str, depth: int = 2) -> dict:
    """
    Explore knowledge graph.

    Args:
        starting_point: Query to find starting point
        depth: Traversal depth

    Returns:
        Dict with 'nodes' and 'edges' lists
    """
    adapter = get_adapter()
    graph = adapter.explore(starting_point, depth)

    return {
        'nodes': [
            {
                'id': n.id,
                'content': n.content,
                'created_at': n.created_at.isoformat(),
                'metadata': n.metadata
            }
            for n in graph.nodes
        ],
        'edges': [
            {
                'source': e.source,
                'target': e.target,
                'type': e.relation_type,
                'metadata': e.metadata
            }
            for e in graph.edges
        ]
    }


def memory_search_facts(query: str, limit: int = 10) -> list:
    """Search for relationships."""
    adapter = get_adapter()
    relationships = adapter.search_facts(query, limit)

    return [
        {
            'source': r.source,
            'target': r.target,
            'type': r.relation_type,
            'metadata': r.metadata
        }
        for r in relationships
    ]


def memory_list_operations() -> list:
    """List available operations."""
    adapter = get_adapter()
    ops = adapter.list_operations()

    return [
        {
            'name': op.name,
            'description': op.description,
            'params': op.params,
            'example': op.example
        }
        for op in ops
    ]


def memory_get_config() -> dict:
    """Get current configuration."""
    adapter = get_adapter()

    return {
        'backend': adapter.config.memory.backend,
        'group_id': adapter.group_id,
        'config_file': 'auto-detected'  # Could track this if needed
    }
