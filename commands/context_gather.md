---
description: Gather comprehensive context from all sources
---

# Context Gather

Use the context-retrieval agent to gather relevant context for a task.

**Task**: $ARGUMENTS

## Implementation

Launch the context-retrieval agent with the task description.

The agent will:
1. Query Graphiti memory backend for relevant information
2. Read linked code artifacts and files
3. Query Context7 for framework documentation
4. Search web if needed

The agent automatically uses Graphiti MCP for memory operations.
