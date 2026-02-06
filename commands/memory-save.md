---
description: Save current conversation context as a memory
---

# Memory Save

Save important context, decisions, or patterns to the knowledge base.

## Your Task

Extract relevant context from the current conversation and save it using the memory adapter.

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save, memory_get_config

# Show config
config = memory_get_config()
print(f"Saving to backend: {config['backend']}, group: {config['group_id']}\n")

# Extract context from conversation
# Analyze the recent messages to determine:
# - What decision was made or pattern discovered
# - Why it matters (importance)
# - Relevant keywords/tags

# Example structure:
title = "<concise title of what's being saved>"
content = """
<detailed description of the context, decision, or pattern>

Include:
- What: The actual decision/pattern/insight
- Why: Rationale or context
- When: Temporal context if relevant
- How: Implementation details if applicable
"""

importance = <1-10 score>  # Only for Forgetful backend
keywords = ["keyword1", "keyword2"]
tags = ["tag1", "tag2"]

# Save the memory
memory_id = memory_save(
    content=content,
    title=title,
    importance=importance,  # Ignored by Graphiti
    keywords=keywords,      # Ignored by Graphiti
    tags=tags              # Ignored by Graphiti
)

print(f"✅ Saved memory with ID: {memory_id}")
print(f"   Title: {title}")
print(f"   Backend: {config['backend']}")
```

## Extraction Guidelines

**What to save:**
- ✅ Architectural decisions and rationale
- ✅ Patterns you've implemented together
- ✅ Important discoveries or insights
- ✅ User preferences and requirements
- ✅ Lessons learned from bugs or issues

**What NOT to save:**
- ❌ Obvious/trivial information
- ❌ Temporary implementation details
- ❌ Information already well-documented elsewhere

**Importance Scoring (for Forgetful):**
- 9-10: Critical decisions, user preferences, major patterns
- 7-8: Important patterns, significant implementations
- 5-6: Useful context, minor decisions
- 1-4: Nice-to-know, low priority

## Response Format

Clearly communicate what was saved:

```
✅ Saved: <title>

Content: <brief summary>
Backend: <graphiti|forgetful>
Group: <group-id>
ID: <memory-id>

This memory will be available for future context retrieval.
```

## Notes

- **No project discovery needed**: Adapter auto-detects group_id from git repo
- **Backend differences**: Graphiti auto-extracts entities, Forgetful uses explicit metadata
- **Atomic memories**: Keep focused on one concept per save
