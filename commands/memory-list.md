---
description: List recent memories from the knowledge base
---

# Memory List

List recent memories to see what context has been saved.

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_list_recent, memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}\n")

# Get count from user input or default to 20
limit = int("$ARGUMENTS") if "$ARGUMENTS".isdigit() else 20

# List recent
memories = memory_list_recent(limit=limit)

print(f"Found {len(memories)} recent memories:\n")

for i, memory in enumerate(memories, 1):
    title = memory['metadata'].get('title', memory['content'][:50])
    print(f"{i}. {title}")
    print(f"   Created: {memory['created_at'][:10]}")
    if memory.get('importance'):
        print(f"   Importance: {memory['importance']}")
    print()
```

## Response Format

Show memories in chronological order (newest first) with:
- Title or content preview
- Creation date
- Importance (if Forgetful backend)
