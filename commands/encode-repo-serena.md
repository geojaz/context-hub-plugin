---
description: Bootstrap a repository into Forgetful's knowledge base using Serena's symbol-level analysis
allowed-tools: mcp__forgetful__discover_forgetful_tools, mcp__forgetful__how_to_use_forgetful_tool, mcp__forgetful__execute_forgetful_tool, mcp__plugin_serena_serena__get_symbols_overview, mcp__plugin_serena_serena__find_symbol, mcp__plugin_serena_serena__find_referencing_symbols, mcp__plugin_serena_serena__list_dir, mcp__plugin_serena_serena__read_file, mcp__plugin_serena_serena__search_for_pattern, mcp__plugin_serena_serena__list_memories, mcp__plugin_serena_serena__read_memory, mcp__plugin_context7_context7__resolve-library-id, mcp__plugin_context7_context7__query-docs, Bash
---

# Encode Repository (Serena-Enhanced)

Systematically populate the Forgetful knowledge base using Serena's LSP-powered symbol analysis for accurate, comprehensive codebase understanding.

## Purpose

Transform an undocumented or lightly-documented codebase into a rich, searchable knowledge repository. Use this when:
- Starting to use Forgetful for an existing project
- Onboarding a new project into the memory system
- Preparing a project for AI agent collaboration
- Creating institutional knowledge for team members
- You want **symbol-accurate architecture mapping** (not regex guessing)

## Why Serena?

Unlike heuristic-based encoding, Serena provides:
- **Accurate symbol extraction** via Language Server Protocol (LSP)
- **Relationship discovery** - find_referencing_symbols shows actual usage
- **Cross-file analysis** - understand how components connect
- **Language-aware parsing** - no regex guessing

## Prerequisites Check (EXECUTE FIRST)

Before proceeding, verify Serena plugin is available:

```bash
claude plugins list | grep -i serena
```

If Serena is not installed:
```
STOP! Serena plugin is required for this command.

Install it with:
  claude plugins install serena

Then re-run /encode-repo-serena
```

Also verify Forgetful MCP is connected by testing:
```
execute_forgetful_tool("list_projects", {})
```

If Forgetful errors, run `/context-hub-setup` first.

## Arguments

$ARGUMENTS

Parse for:
- **Project path**: Directory to encode (default: current working directory)
- **Project name**: Override auto-detected name (optional)
- **Phases**: Specific phases to run (optional, default: all)

---

## Memory Targets by Project Profile

| Profile | Phase 1 | Phase 1B | Phase 2 | Phase 2B | Phase 3 | Phase 4 | Phase 5 | Total |
|---------|---------|----------|---------|----------|---------|---------|---------|-------|
| Small Simple | 3-5 | 1-2 | 3-5 | 3-5 entities | 3-5 | 2-4 | 2-3 | 15-27 memories + entities |
| Small Complex | 5-7 | 1-2 | 5-8 | 5-10 entities | 5-8 | 4-6 | 3-5 | 26-42 memories + entities |
| Medium Standard | 5-10 | 1-2 | 10-15 | 10-20 entities | 8-12 | 5-10 | 5-8 | 35-60 memories + entities |
| Large | 8-12 | 2-3 | 15-20 | 20-40 entities | 12-18 | 10-15 | 8-12 | 60-100 memories + entities |

**Notes**:
- Phase 1B creates 1-3 dependency memories per project
- Phase 2B creates entities (not memories) for components and their relationships
- Serena-enhanced encoding may discover more architectural detail, potentially exceeding these targets

---

## Phase 0: Discovery & Assessment (ALWAYS START HERE)

### Step 1: Activate Project in Serena

First, check if Serena has any existing memories for this project:

```
mcp__plugin_serena_serena__list_memories()
```

Read any relevant memories to understand previous analysis.

### Step 2: Explore Project Structure

```
mcp__plugin_serena_serena__list_dir({
  "relative_path": ".",
  "recursive": true,
  "skip_ignored_files": true
})
```

### Step 3: Check Existing Forgetful Coverage

```
execute_forgetful_tool("list_projects", {})
```

If project exists, query existing memories:
```
execute_forgetful_tool("query_memory", {
  "query": "<project-name> architecture",
  "query_context": "Assessing KB coverage before Serena bootstrap",
  "k": 10,
  "project_ids": [<project_id>]
})
```

### Step 4: Analyze Entry Points

Read key files to understand project:
```
mcp__plugin_serena_serena__read_file({"relative_path": "README.md"})
mcp__plugin_serena_serena__read_file({"relative_path": "pyproject.toml"})
# or package.json, Cargo.toml, etc.
```

### Step 5: Gap Analysis

Compare:
- What's in Forgetful KB?
- What exists in codebase?
- What's missing?

Report findings before proceeding.

---

## Phase 1: Project Foundation (5-10 memories)

### Create/Update Project in Forgetful

If project doesn't exist:
```
execute_forgetful_tool("create_project", {
  "name": "owner/repo-name",
  "description": "<problem solved, features, tech stack>",
  "project_type": "development",
  "repo_name": "owner/repo"
})
```

### Create Foundation Memories

1. **Project Overview** (Importance: 10)
2. **Technology Stack** (Importance: 9)
3. **Architecture Pattern** (Importance: 10)
4. **Development Setup** (Importance: 8)
5. **Testing Strategy** (Importance: 8)

---

## Phase 1B: Dependency Analysis

**Purpose**: Extract and document project dependencies systematically, validating assumptions with Context7.

### Step 1: Detect Manifest Files

Look for dependency manifests:
```
mcp__plugin_serena_serena__find_file({
  "file_mask": "package.json",
  "relative_path": "."
})
```

Common manifests to check:
- `package.json` (Node.js)
- `pyproject.toml`, `requirements.txt`, `Pipfile` (Python)
- `Cargo.toml` (Rust)
- `go.mod` (Go)
- `Gemfile` (Ruby)
- `pom.xml`, `build.gradle` (Java)

### Step 2: Parse Dependencies

Read manifest and extract:
- Direct dependencies (name, version)
- Dev dependencies
- Categorize by role: framework, library, database, tool

### Step 3: Validate with Context7 (Major Frameworks Only)

For core frameworks (FastAPI, React, PostgreSQL, etc.), validate usage assumptions:
```
mcp__plugin_context7_context7__resolve-library-id({
  "libraryName": "fastapi",
  "query": "How does FastAPI handle dependency injection?"
})
```

Then query specific patterns observed in the repo:
```
mcp__plugin_context7_context7__query-docs({
  "libraryId": "/tiangolo/fastapi",
  "query": "Depends pattern for request validation"
})
```

Use Context7 to confirm:
- Observed usage patterns are correct
- No deprecated APIs being used
- Best practices being followed

### Step 4: Create Dependency Memory

```
execute_forgetful_tool("create_memory", {
  "title": "[Project] - Dependencies and External Libraries",
  "content": "Language: [lang] [version]. Core frameworks: [list with roles].
              Data/storage: [databases]. HTTP/API: [frameworks].
              Dev tools: [testing, linting, build].
              Rationale: [why chosen, if documented].",
  "context": "Understanding technology choices and integration patterns",
  "keywords": ["tech-stack", "dependencies", "frameworks", "libraries"],
  "tags": ["technology", "foundation", "dependencies"],
  "importance": 9,
  "project_ids": [<project_id>]
})
```

---

## Phase 2: Symbol-Level Architecture (10-15 memories)

**This is where Serena shines.**

### Step 1: Get Symbol Overview for Key Files

For each major source file:
```
mcp__plugin_serena_serena__get_symbols_overview({
  "relative_path": "src/main.py",
  "depth": 1
})
```

This returns classes, functions, methods with their locations.

### Step 2: Analyze Key Classes/Modules

For important symbols discovered:
```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "ClassName",
  "include_body": false,
  "depth": 1
})
```

### Step 3: Discover Relationships

For core classes/functions:
```
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "ClassName/method_name",
  "relative_path": "src/module.py"
})
```

This reveals:
- Who calls this method?
- Where is this class used?
- What depends on what?

### Step 4: Create Architecture Memories

For each architectural layer discovered:
```
{
  "title": "[Project] - [Layer] Architecture",
  "content": "Key symbols: [list]. Relationships: [discovered references]. Pattern: [identified pattern].",
  "context": "Discovered via Serena symbol analysis",
  "importance": 8,
  "tags": ["architecture"]
}
```

---

## Phase 2B: Entity Graph Creation

**Purpose**: Build a knowledge graph of project components and their relationships in Forgetful.

### Entity Deduplication (ALWAYS CHECK FIRST)

Before creating any entity, check if it already exists:
```
execute_forgetful_tool("search_entities", {
  "query": "<entity-name>",
  "limit": 5
})
```

The search checks both `name` and `aka` (aliases) fields.

- **If found**: Use existing entity ID, optionally update notes/tags
- **If not found**: Create with comprehensive `aka` list for future matching

### Standard Entity Types

Use `entity_type: "other"` with these `custom_type` values (allow flexibility for non-standard cases):
- `Library` - external packages/dependencies (npm, pip, cargo packages)
- `Service` - backend services, APIs, microservices
- `Component` - major code components, modules
- `Tool` - build tools, CLI tools, parsers
- `Framework` - core frameworks (or use `entity_type: "organization"`)

### Entity Creation Criteria

Only create entities for **major components**:
- High reference count from Serena (agent judges "high" based on project size)
- Core architectural components (services, modules with many dependents)
- External dependencies central to the project
- Services/modules that other components depend on

### Tagging Strategy

- Use `project_ids` for scoping (no discovery-method tags)
- Tag by role: `library`, `service`, `component`, `database`, `framework`, `tool`
- Tag by domain if relevant: `auth`, `api`, `storage`, `ui`, `config`

### Step 1: Create Entities for Major Components

For each major component discovered via Serena:
```
execute_forgetful_tool("create_entity", {
  "name": "AuthenticationService",
  "entity_type": "other",
  "custom_type": "Service",
  "notes": "Centralized auth service. Location: src/services/auth.py.
            Handles token validation, user context injection.",
  "tags": ["service", "auth"],
  "aka": ["AuthService", "auth", "auth_service"],
  "project_ids": [<project_id>]
})
```

### Step 2: Create Entities for Key Dependencies

For external libraries central to the project:
```
execute_forgetful_tool("create_entity", {
  "name": "FastAPI",
  "entity_type": "other",
  "custom_type": "Framework",
  "notes": "Python async web framework. Used for REST API and WebSocket endpoints.",
  "tags": ["framework", "api"],
  "aka": ["fastapi", "fast-api", "fast_api"],
  "project_ids": [<project_id>]
})
```

### Step 3: Create Relationships

Map how components connect using reference counts from Serena:
```
execute_forgetful_tool("create_entity_relationship", {
  "source_entity_id": <project_or_component_id>,
  "target_entity_id": <library_id>,
  "relationship_type": "uses",
  "strength": 1.0,
  "metadata": {
    "version": "0.104.1",
    "role": "HTTP framework and routing"
  }
})
```

**Relationship types**:
- `uses` - project/component uses library
- `depends_on` - component depends on another
- `calls` - service calls another service
- `extends` - class extends base class
- `implements` - class implements interface
- `connects_to` - system connects to database/service

**Strength calculation**:
- Based on Serena reference count
- Normalize to 0.0-1.0 scale within project
- Higher reference count = higher strength

### Step 4: Link Entities to Memories

Connect entities to their architecture memories:
```
execute_forgetful_tool("link_entity_to_memory", {
  "entity_id": <component_entity_id>,
  "memory_id": <architecture_memory_id>
})
```

This enables bidirectional discovery:
- Find entity → get related memories
- Query memories → discover linked entities

---

## Phase 3: Pattern Discovery (8-12 memories)

### Search for Common Patterns

```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "async def",
  "restrict_search_to_code_files": true,
  "context_lines_before": 2,
  "context_lines_after": 5
})
```

Useful patterns to search:
- Error handling: `except|catch|Error`
- Dependency injection: `Depends|@inject|Container`
- Decorators: `@app\.|@router\.|@middleware`
- Database patterns: `session|transaction|commit`

### Analyze Pattern Usage

For each pattern found, use symbol analysis:
```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "pattern_name",
  "substring_matching": true,
  "include_body": true
})
```

### Create Pattern Memories

Document recurring patterns with actual code locations and usage counts.

---

## Phase 4: Critical Features (1-2 per feature)

### Identify Features via Symbol Analysis

Look for route handlers, API endpoints, main workflows:
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "@(app|router)\\.(get|post|put|delete)",
  "restrict_search_to_code_files": true
})
```

### Trace Feature Flow

For each feature:
1. Find the entry point symbol
2. Use `find_referencing_symbols` to trace downstream
3. Document the complete flow in a memory

---

## Phase 5: Design Decisions (from documentation only)

**CRITICAL: Only capture explicitly documented decisions.**

Search for decision documentation:
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Decision:|Rationale:|## Why|ADR-",
  "paths_include_glob": "**/*.md"
})
```

If found, create decision memories. If not, skip this phase.

---

## Phase 6: Code Artifacts

For reusable patterns discovered via Serena:
```
execute_forgetful_tool("create_code_artifact", {
  "title": "Descriptive name",
  "description": "What it does and when to use it",
  "code": "<implementation from find_symbol with include_body=true>",
  "language": "python",
  "tags": ["pattern", "<domain-tag>"],
  "project_id": <project_id>
})
```

---

## Phase 7: Documents (as needed)

For content >400 words (detailed guides, comprehensive analysis):
```
execute_forgetful_tool("create_document", {
  "title": "Document name",
  "description": "Overview and purpose",
  "content": "<full documentation>",
  "document_type": "markdown",
  "project_id": <project_id>
})
```

Create 3-5 atomic memories as entry points, linked via `document_ids`.

---

## Phase 8: Serena Memory (Optional)

Save key findings to Serena's memory for future analysis:
```
mcp__plugin_serena_serena__write_memory({
  "memory_file_name": "project-analysis.md",
  "content": "# [Project] Analysis Summary\n\n## Key Symbols\n..."
})
```

This helps future Serena sessions understand the project faster.

---

## Execution Guidelines

1. **Execute phases in order**: 0 → 1 → 1B → 2 → 2B → 3 → 4 → 5 → 6 → 7 → 8
2. **Leverage Serena's strengths**: Symbol analysis over text search
3. **Track relationships**: find_referencing_symbols is powerful - use it
4. **Deduplicate entities**: Always search before creating
5. **Use Context7**: Validate framework usage assumptions
6. **Skip phases** with good existing coverage
7. **Update outdated memories** as discovered
8. **Link new memories** to existing related memories
9. **Link entities to memories**: Enable bidirectional discovery
10. **Mark obsolete** memories that reference removed code

## Quality Principles

- **Symbol-accurate**: Use LSP data, not guesses
- **Relationship-aware**: Document how things connect
- **One concept per memory** (atomic)
- **200-400 words ideal** per memory
- **Include context field** explaining relevance
- **Honest importance scoring** (most should be 7-8)
- **Quality over quantity**
- **Only document what's explicitly in the repo** (especially for decisions)

---

## Validation

After completion, verify coverage:

### Test Memories
```
execute_forgetful_tool("query_memory", {
  "query": "How do I add a new API endpoint?",
  "query_context": "Testing Serena bootstrap coverage",
  "project_ids": [<project_id>]
})
```

### Test Dependencies
```
execute_forgetful_tool("query_memory", {
  "query": "What dependencies does this project use?",
  "query_context": "Validating dependency encoding",
  "project_ids": [<project_id>]
})
```

### Test Entities (scoped by project)
```
execute_forgetful_tool("list_entities", {
  "project_ids": [<project_id>]
})
```

### Test Entities by Role
```
execute_forgetful_tool("list_entities", {
  "project_ids": [<project_id>],
  "tags": ["library"]
})
```

### Test Relationships
```
execute_forgetful_tool("get_entity_relationships", {
  "entity_id": <component_entity_id>,
  "direction": "outgoing"
})
```

Test with architecture questions - Serena-encoded repos should answer accurately.

---

## Report Progress

After each phase:
- Symbols analyzed
- Memories created/updated
- Relationships discovered
- Gaps remaining

Ask user to confirm before proceeding.
