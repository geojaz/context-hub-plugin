"""Unified data models for memory operations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Memory:
    """Unified memory representation across backends."""
    id: str
    content: str
    created_at: datetime
    importance: Optional[int] = None  # Forgetful has this, Graphiti infers it
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """Relationship between entities in knowledge graph."""
    source: str
    target: str
    relation_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """Graph of memories and their relationships."""
    nodes: List[Memory]
    edges: List[Relationship]


@dataclass
class OperationInfo:
    """Information about available memory operations."""
    name: str
    description: str
    params: Dict[str, str]
    example: str
