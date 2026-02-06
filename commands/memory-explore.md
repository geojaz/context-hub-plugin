---
description: Deep exploration of the knowledge graph
---

# Memory Explore

Traverse the knowledge graph from a starting point to discover connected concepts.

**Query**: $ARGUMENTS

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_explore, memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}\n")

# Explore from starting point
graph = memory_explore("$ARGUMENTS", depth=2)

print(f"Explored knowledge graph from: $ARGUMENTS\n")
print(f"Found {len(graph['nodes'])} nodes and {len(graph['edges'])} connections\n")

# Show nodes
print("Key Concepts:")
for node in graph['nodes'][:5]:
    title = node['metadata'].get('title', node['content'][:50])
    print(f"  - {title}")

print(f"\nConnections: {len(graph['edges'])} relationships discovered")

# Show some relationships
for edge in graph['edges'][:5]:
    print(f"  {edge['source']} --[{edge['type']}]--> {edge['target']}")
```

## Notes

- **Graphiti**: Native graph traversal via search_facts
- **Forgetful**: Manual traversal via linked_memory_ids
- Depth=2 explores 2 levels of connections
