---
description: Gather comprehensive context from all sources
---

# Context Gather

Use the context-retrieval agent with memory adapter integration.

**Task**: $ARGUMENTS

## Implementation

Launch the context-retrieval agent with the task description.

The agent will:
1. Query memory backend (auto-selected: Graphiti or Forgetful)
2. Read linked code artifacts and files
3. Query Context7 for framework docs
4. Search web if needed

The agent has been updated to use the memory adapter automatically.
