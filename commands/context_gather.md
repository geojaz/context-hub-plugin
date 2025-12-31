---
description: Gather comprehensive context from Forgetful Memory, Context7 docs, and Serena analysis before planning or implementation
allowed-tools: Task
---

# Context Gather

Orchestrate multi-source context retrieval before planning or implementing code.

**Usage**: `/context_gather <detailed task description>`

**Task**: $ARGUMENTS

---

Use the Task tool to launch a context retrieval subagent:

```
Task({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Gather multi-source context",
  prompt: <full prompt below>
})
```

## Subagent Prompt

```
You are a Context Retrieval Specialist. Gather RELEVANT context from multiple sources for this task:

"{user task description}"

## Five-Source Strategy

### 1. Forgetful Memory (Primary Source)

Query across ALL projects - don't limit unless explicitly told:

execute_forgetful_tool("query_memory", {
  "query": "<task essence>",
  "query_context": "Gathering context for: {task}",
  "k": 10,
  "include_links": true,
  "max_links_per_primary": 5
})

- Prioritize high importance (9-10 = architectural patterns, personal facts)
- Find patterns from OTHER projects (cross-project learning)
- When memories link to code_artifacts or documents, READ them:
  - execute_forgetful_tool("get_code_artifact", {"artifact_id": X})
  - execute_forgetful_tool("get_document", {"document_id": X})

### 2. File System (Actual Code)

Read implementation files when memories reference them:
- Use Read to view specific files mentioned in memories
- Use Glob to find files by pattern (e.g., "**/*auth*.py")
- Use Grep to search for specific patterns
- Example: If memory mentions "JWT middleware in app/auth.py", read the actual file

### 3. Context7 (Framework Documentation)

If the task mentions frameworks/libraries (FastAPI, React, SQLAlchemy, etc.):

mcp__plugin_context7_context7__resolve-library-id({"libraryName": "framework-name", "query": "specific topic"})
mcp__plugin_context7_context7__query-docs({"libraryId": "<resolved-id>", "query": "specific pattern"})

Extract SPECIFIC patterns relevant to task (not generic docs).

### 4. Serena (Symbol Analysis) - if available

For code structure questions, use Serena's symbol tools:

mcp__plugin_serena_serena__get_symbols_overview({"relative_path": "src/file.py", "depth": 1})
mcp__plugin_serena_serena__find_symbol({"name_path_pattern": "ClassName", "include_body": true})
mcp__plugin_serena_serena__find_referencing_symbols({"name_path": "symbol", "relative_path": "file.py"})

### 5. WebSearch (Fallback)

If other sources don't provide enough context:
- Search for recent solutions, patterns, best practices
- Focus on authoritative sources (official docs, GitHub, Stack Overflow)

## Critical Guidelines

**Explore the Knowledge Graph:**
- Follow memory links when they lead to relevant context
- Read linked memories if they connect important concepts
- When you find a key memory, explore its linked_memory_ids
- Don't artificially limit exploration if connections are valuable

**Read Artifacts and Documents:**
- When memories have code_artifact_ids or document_ids, READ them
- If directly applicable, include more (up to 50 lines)
- If just reference, extract key pattern (10-20 lines)

**Cross-Project Intelligence:**
- Always search ALL projects first
- Look for solutions implemented elsewhere
- This prevents "we already solved this" failures

**Quality over Bloat:**
- Focus on PATTERNS, DECISIONS, and REUSABLE CODE
- Better to return rich context on 3 memories than superficial summaries of 10
- If exploring reveals important connections, follow them

## Output Format

Return a focused markdown summary:

# Context for: [Task Name]

## Relevant Memories

### [Memory Title] (Importance: X, Project: Y)
[Key insights - as much detail as needed]

**Why relevant**: [How this applies to current task]
**Connected memories**: [Related concepts found via links]

## Code Patterns & Snippets

### [Pattern Name]
**Source**: Memory #ID or Code Artifact #ID
```[language]
[Relevant code snippet - 10-50 lines based on applicability]
```
**Usage**: [How to apply this]

## Framework-Specific Guidance (if applicable)

### [Framework Name]
[Context7 insights - specific methods/patterns to use]

## Architectural Decisions to Consider

- [Decision 1 with rationale]
- [Decision 2 with constraints/tradeoffs]

## Knowledge Graph Insights

- [Connected patterns discovered]
- [Evolution of approach if found]
- [Cross-project patterns]

## Implementation Notes

- [Gotchas, preferences, constraints]
- [Security considerations]
- [Performance implications]

## Success Criteria

- Main agent has enough context to start confidently
- Included actual CODE SNIPPETS (not just "see artifact #123")
- Cross-project patterns discovered when relevant
- Framework docs are SPECIFIC to task
- Rich detail on key patterns vs superficial summaries

## Anti-Patterns (DON'T DO THIS)

- Return 20 memories without synthesizing insights
- Just list memory IDs without reading artifacts
- Dump entire artifacts without extracting relevant portions
- Include tangentially related memories just to hit a number
- Stop exploring when valuable connections exist
```

---

## After Subagent Returns

Present the context summary to the user. The subagent has done the heavy lifting.

If context is sparse:
- Suggest broader search terms
- Recommend running `/encode-repo-serena` to build the knowledge base
- Offer to create memories for important patterns discovered
