# Context Hub Memory Adapter Library

Python library for pluggable memory backend support.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from lib import MemoryAdapter

# Initialize (auto-detects config and group_id)
adapter = MemoryAdapter()

# Query memories
memories = adapter.query("authentication patterns", limit=10)

# Save a memory
memory_id = adapter.save(
    "Decision: Using JWT for auth",
    title="Auth Decision"
)

# Explore knowledge graph
graph = adapter.explore("authentication", depth=2)
```

## Configuration

Create `.context-hub.yaml` in project root:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # auto-detect from git or set explicitly
```

## Backend Support

- **Graphiti**: Knowledge graph with automatic entity extraction
- **Forgetful**: Atomic memories with manual linking

## Architecture

```
MemoryAdapter
 ├── ConfigManager (hierarchical config discovery)
 ├── GraphitiBackend (mcp__graphiti__* tools)
 └── ForgetfulBackend (mcp__forgetful__* tools)
```

See `examples/basic_usage.py` for detailed examples.
