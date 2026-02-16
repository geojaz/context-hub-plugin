# User-Level Group ID with Flexible Repo Tagging

**Date**: 2026-02-16
**Status**: Design Complete

## Problem

Current graphiti-context-hub implementation auto-detects `group_id` per repository, causing:
- Memory fragmentation across repos
- Difficulty searching across projects
- Inconsistent group_id usage by Claude
- Can't leverage cross-repo patterns

## Solution

Migrate to single user-level `group_id` with flexible repo tagging via Graphiti's entity extraction.

## Design Decisions

### 1. Single Global Group ID

**Choice**: One `group_id = "main"` for all repositories.

**Rationale**:
- Memories naturally connect across projects
- Patterns learned in one repo inform work in others
- Simpler mental model - one knowledge graph
- No context switching between repos

**Alternative Rejected**: Multiple group_ids per context (work/personal) - adds unnecessary complexity.

### 2. Configuration Location

**Global Config**: `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
```

**Fallback Chain**:
1. Global config: `~/.config/claude/graphiti-context-hub.conf`
2. Local config: `.context-hub.conf` (overrides global if present)
3. Environment: `GRAPHITI_GROUP_ID`
4. Default: `"main"`

**Format**: Shell-sourceable config (no Python dependencies like yaml)

### 3. Repository Tagging

**Approach**: Embed repo context in episode body as structured text.

**Format**:
```
Repo: {repo_name}

{actual_content}
```

**Example**:
```
Repo: graphiti-context-hub

Decision: Migrated to user-level group_id

Rationale:
- Eliminates cross-repo fragmentation
- Enables knowledge sharing across projects
```

**How It Works**:
- Graphiti automatically extracts "graphiti-context-hub" as an entity
- Creates relationships between repo and concepts
- Enables searches like: "authentication in repo graphiti-context-hub"
- Shows cross-repo patterns: "authentication used in [repo1, repo2, repo3]"

**Benefits**:
- No rigid schema - just text Graphiti indexes
- Can search by repo or across all repos
- See which projects share patterns
- Flexible - can add more context (branch, commit, etc.) later

### 4. Implementation: Pure Bash + MCP Tools

**No Python Dependencies**: Avoid yaml, subprocess in Python.

**Inline Bash Helper** (used in skills/commands):

```bash
# Load config and detect repo
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Then call MCP tool directly**:

```python
mcp__graphiti__add_memory({
    "name": "Decision: Added authentication",
    "episode_body": f"""Repo: {REPO_NAME}

Decision: Implemented JWT authentication

Rationale: XSS protection, CSRF protection
""",
    "group_id": GROUP_ID,  # Always "main"
    "source": "context-hub"
})
```

**Why Bash**:
- Git already available in dev environments
- No dependency on Python packages (yaml, etc.)
- Simple shell config file
- MCP tools called natively by Claude

### 5. Save Patterns

**Primary: Proactive/Automatic** (90% of saves)
- Claude saves during work when skills guide it
- User says conversationally: "remember I prefer strict TypeScript"
- No prompting - just saves

**Secondary: Manual Command** (10% of saves)
- `/memory-save` - saves current conversation context
- Rarely used - most saves happen naturally

### 6. Migration Strategy

**Choice**: Fresh start with `group_id="main"`

**Approach**:
- Old memories stay in repo-specific groups (preserved)
- New memories use `group_id="main"` with repo tagging
- Old memories not searched (clean slate)

**Rationale**:
- Simplest migration path
- No complex data transformation
- Old data preserved if needed later
- Start building unified knowledge graph immediately

**Alternative Rejected**: Migrate all episodes to "main" - requires Graphiti API support for bulk updates, complex.

## Architecture

### Configuration Flow

```
┌─────────────────────────────────────────┐
│ ~/.config/claude/                       │
│   graphiti-context-hub.conf             │
│   (GRAPHITI_GROUP_ID=main)              │
└─────────────┬───────────────────────────┘
              │
              ↓ (can be overridden by)
┌─────────────────────────────────────────┐
│ /path/to/repo/.context-hub.conf         │
│ (local override, optional)              │
└─────────────┬───────────────────────────┘
              │
              ↓ (can be overridden by)
┌─────────────────────────────────────────┐
│ GRAPHITI_GROUP_ID env variable          │
└─────────────┬───────────────────────────┘
              │
              ↓ (defaults to)
         "main"
```

### Memory Structure in Graphiti

```
Episode:
  group_id: "main"
  name: "Decision: Added authentication"
  body: "Repo: graphiti-context-hub\n\nDecision: ..."

Graphiti Extracts:
  - Entity: "graphiti-context-hub" (type: repository)
  - Entity: "authentication"
  - Relationship: graphiti-context-hub → uses → authentication
```

### Search Patterns

**By repository**:
```python
mcp__graphiti__search_memory_facts({
    "query": "authentication in graphiti-context-hub",
    "group_ids": ["main"],
    "max_facts": 20
})
```

**Across all repositories**:
```python
mcp__graphiti__search_memory_facts({
    "query": "authentication patterns",
    "group_ids": ["main"],
    "max_facts": 20
})
```

**Which repos use a pattern**:
```python
# Graphiti relationships show:
# authentication → used-in → [repo1, repo2, repo3]
```

## Implementation Changes

### New Files

- `~/.config/claude/graphiti-context-hub.conf` - Global config (created by setup)

### Modified Files

**Commands** (update all to use Bash helper):
- `commands/memory-search.md`
- `commands/memory-list.md`
- `commands/memory-save.md`
- `commands/memory-explore.md`
- `commands/encode-repo-serena.md`
- `commands/context_gather.md`
- `commands/context-hub-setup.md` - Create global config

**Skills** (update config loading pattern):
- `skills/using-graphiti-memory/SKILL.md`
- `skills/exploring-knowledge-graph/SKILL.md`
- `skills/serena-code-architecture/SKILL.md`

**Documentation**:
- `README.md` - Document global config approach
- `.context-hub.yaml.example` - Show local override option

### Updated Behavior

**Before**:
- `group_id` = auto-detected repo name
- Memories isolated per repo
- `Project: {repo_name}` prefix

**After**:
- `group_id` = "main" (always)
- Memories shared across repos
- `Repo: {repo_name}` prefix
- Graphiti extracts repo as entity

## Benefits

✅ **Unified Knowledge Graph**: One graph across all projects
✅ **Cross-Repo Patterns**: See patterns used in multiple repos
✅ **Flexible Tagging**: Graphiti entity extraction, no rigid schema
✅ **No Python Dependencies**: Pure Bash + MCP tools
✅ **Simple Config**: One global setting, works everywhere
✅ **Local Overrides**: Can still override per-repo if needed
✅ **Clean Migration**: Fresh start, old data preserved

## Success Criteria

- [ ] Global config file creation via `/context-hub-setup`
- [ ] All commands use Bash helper for config loading
- [ ] All memories include `Repo: {repo_name}` in episode body
- [ ] Can search by repo: "auth in graphiti-context-hub"
- [ ] Can search globally: "auth patterns" finds across repos
- [ ] Skills guide Claude to save with repo context
- [ ] Documentation updated
- [ ] Local override still works (`.context-hub.conf`)

## Next Steps

1. Create implementation plan with task breakdown
2. Update `/context-hub-setup` to create global config
3. Update all commands with Bash helper pattern
4. Update skills with new save pattern
5. Update documentation
6. Test in multiple repos
