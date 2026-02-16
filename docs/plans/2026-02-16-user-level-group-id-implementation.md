# User-Level Group ID Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate graphiti-context-hub to use single user-level group_id="main" with Bash-based config loading and repo tagging.

**Architecture:** Replace Python YAML config loading with Bash-sourceable config files. Global config in `~/.config/claude/`, local overrides in repo. Embed repo name in episode bodies for Graphiti entity extraction.

**Tech Stack:** Bash, Graphiti MCP tools, markdown commands

---

## Task 1: Update Config File Format

**Files:**
- Modify: `.context-hub.yaml`
- Create: `.context-hub.conf`
- Create: `.context-hub.conf.example`

**Step 1: Create new Bash config format**

Create `.context-hub.conf`:
```bash
# Graphiti Context Hub Configuration
# This file is sourced by Bash - use shell variable syntax

# Group ID for Graphiti knowledge graph
# Default: "main" (single unified graph across all repos)
GRAPHITI_GROUP_ID=main

# Graphiti MCP endpoint (optional)
# Default: http://localhost:8000
GRAPHITI_ENDPOINT=http://localhost:8000
```

**Step 2: Create example config**

Create `.context-hub.conf.example`:
```bash
# Graphiti Context Hub Configuration Example
# Copy to .context-hub.conf to customize

# Group ID for Graphiti knowledge graph
# Use "main" for unified cross-repo knowledge graph (recommended)
# Or set custom value for repo-specific isolation
GRAPHITI_GROUP_ID=main

# Graphiti MCP endpoint (optional)
GRAPHITI_ENDPOINT=http://localhost:8000
```

**Step 3: Keep YAML for backward compatibility**

Update `.context-hub.yaml`:
```yaml
# DEPRECATED: This format is still supported but .context-hub.conf is preferred
# Bash config (.context-hub.conf) will override this if present

graphiti:
  group_id: "main"  # Changed from "auto" to "main"
  endpoint: "http://localhost:8000"
```

**Step 4: Commit**

```bash
git add .context-hub.conf .context-hub.conf.example .context-hub.yaml
git commit -m "refactor: add Bash config format for group_id"
```

---

## Task 2: Update /context-hub-setup Command

**Files:**
- Modify: `commands/context-hub-setup.md`

**Step 1: Replace Python config check with Bash**

Replace the config checking section (lines 74-99) with:

```markdown
**Step 2: Create or verify global config**

```bash
# Create global config directory
mkdir -p "$HOME/.config/claude"

GLOBAL_CONFIG="$HOME/.config/claude/graphiti-context-hub.conf"

if [ -f "$GLOBAL_CONFIG" ]; then
    echo "✓ Global config exists: $GLOBAL_CONFIG"
    source "$GLOBAL_CONFIG"
    echo "  GRAPHITI_GROUP_ID=${GRAPHITI_GROUP_ID:-main}"
    echo "  GRAPHITI_ENDPOINT=${GRAPHITI_ENDPOINT:-http://localhost:8000}"
else
    echo "Creating global config..."
    cat > "$GLOBAL_CONFIG" << 'EOF'
# Graphiti Context Hub Configuration
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
EOF
    echo "✓ Created $GLOBAL_CONFIG"
    echo "  GRAPHITI_GROUP_ID=main"
    echo "  GRAPHITI_ENDPOINT=http://localhost:8000"
fi

echo ""
```

**Step 2: Update local config check**

Add after global config section:

```markdown
**Step 3: Check local config (optional)**

```bash
LOCAL_CONFIG=".context-hub.conf"

if [ -f "$LOCAL_CONFIG" ]; then
    echo "✓ Local config exists (overrides global)"
    source "$LOCAL_CONFIG"
    echo "  GRAPHITI_GROUP_ID=${GRAPHITI_GROUP_ID}"
else
    echo "ℹ No local config (using global settings)"
    echo "  To override: cp .context-hub.conf.example .context-hub.conf"
fi

echo ""
```

**Step 3: Update repo detection**

Replace Python repo detection with:

```markdown
**Step 4: Detect repository context**

```bash
if git remote get-url origin &>/dev/null; then
    REPO_NAME=$(git remote get-url origin | sed 's/.*\///' | sed 's/\.git$//')
else
    REPO_NAME=$(basename "$PWD")
fi

echo "Detected repository: $REPO_NAME"
echo "Using group_id: ${GRAPHITI_GROUP_ID:-main}"
echo ""
```

**Step 4: Test Graphiti connection**

Keep MCP tool test as-is (Python block calling `mcp__graphiti__get_status`).

**Step 5: Commit**

```bash
git add commands/context-hub-setup.md
git commit -m "refactor: update context-hub-setup for Bash config"
```

---

## Task 3: Update /memory-search Command

**Files:**
- Modify: `commands/memory-search.md`

**Step 1: Replace Python config loading with Bash**

Replace Step 1 (lines 15-57) with:

```markdown
**Step 1: Load config and detect repo**

```bash
# Load global config
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"

# Load local config (overrides global)
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

# Set default
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"

# Detect repo name
if git remote get-url origin &>/dev/null; then
    REPO_NAME=$(git remote get-url origin | sed 's/.*\///' | sed 's/\.git$//')
else
    REPO_NAME=$(basename "$PWD")
fi

echo "Searching in group_id: $GROUP_ID"
echo "Current repo: $REPO_NAME"
echo ""
```

**Step 2: Pass GROUP_ID to Python**

Update Step 2 to use GROUP_ID from Bash output:

```markdown
**Step 2: Search Graphiti**

Using the GROUP_ID from Step 1, search the knowledge graph:

```python
query = "$ARGUMENTS"

# GROUP_ID comes from Bash output above
result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [GROUP_ID],  # Now always "main"
    "max_nodes": 10
})
```

**Step 3: Commit**

```bash
git add commands/memory-search.md
git commit -m "refactor: memory-search uses Bash config loading"
```

---

## Task 4: Update /memory-save Command

**Files:**
- Modify: `commands/memory-save.md`

**Step 1: Replace config loading**

Replace the config loading section with Bash helper:

```markdown
**Step 1: Load config and detect repo**

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

echo "group_id: $GROUP_ID"
echo "repo: $REPO_NAME"
```

**Step 2: Update save pattern with repo tagging**

Replace the save step to include repo in episode_body:

```markdown
**Step 2: Save to Graphiti with repo context**

Ask user what to save (title and content), then:

```python
# Format episode body with repo prefix
episode_body = f"""Repo: {REPO_NAME}

{content_from_user}
"""

# Save episode using GROUP_ID from Bash
result = mcp__graphiti__add_memory({
    "name": title_from_user,
    "episode_body": episode_body,
    "group_id": GROUP_ID,
    "source": "context-hub",
    "source_description": f"Manual save from {REPO_NAME}"
})

episode_id = result.get('episode_id', result.get('uuid', 'unknown'))
print(f"✓ Saved to group '{GROUP_ID}' with repo tag '{REPO_NAME}'")
print(f"  Episode ID: {episode_id}")
```

**Step 3: Commit**

```bash
git add commands/memory-save.md
git commit -m "refactor: memory-save uses Bash config and repo tagging"
```

---

## Task 5: Update /memory-list Command

**Files:**
- Modify: `commands/memory-list.md`

**Step 1: Replace config loading**

Same Bash helper pattern:

```markdown
**Step 1: Load config**

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
echo "Listing episodes from group: $GROUP_ID"
```

**Step 2: Use GROUP_ID in MCP call**

```python
limit = int("$ARGUMENTS".strip()) if "$ARGUMENTS".strip().isdigit() else 20

result = mcp__graphiti__get_episodes({
    "group_ids": [GROUP_ID],
    "max_episodes": limit
})
```

**Step 3: Commit**

```bash
git add commands/memory-list.md
git commit -m "refactor: memory-list uses Bash config loading"
```

---

## Task 6: Update /memory-explore Command

**Files:**
- Modify: `commands/memory-explore.md`

**Step 1: Replace config loading**

Same Bash helper:

```markdown
**Step 1: Load config**

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

echo "Exploring group: $GROUP_ID"
echo "Current repo: $REPO_NAME"
```

**Step 2: Update MCP calls**

Use GROUP_ID from Bash output in both search calls.

**Step 3: Commit**

```bash
git add commands/memory-explore.md
git commit -m "refactor: memory-explore uses Bash config loading"
```

---

## Task 7: Update /encode-repo-serena Command

**Files:**
- Modify: `commands/encode-repo-serena.md`

**Step 1: Replace config loading**

```markdown
**Step 1: Load config and detect repo**

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

echo "Encoding repo: $REPO_NAME"
echo "Into group: $GROUP_ID"
```

**Step 2: Update episode format with repo tagging**

Update the save loop to include repo prefix:

```python
episode_content = f"""Repo: {REPO_NAME}
File: {file_path}

Symbols:
{symbols}
"""

result = mcp__graphiti__add_memory({
    "name": f"Architecture: {file_path}",
    "episode_body": episode_content,
    "group_id": GROUP_ID,
    "source": "serena-encode",
    "source_description": f"Repository encoding: {REPO_NAME}"
})
```

**Step 3: Commit**

```bash
git add commands/encode-repo-serena.md
git commit -m "refactor: encode-repo-serena uses Bash config and repo tagging"
```

---

## Task 8: Update using-graphiti-memory Skill

**Files:**
- Modify: `skills/using-graphiti-memory/SKILL.md`

**Step 1: Replace "How to Query" section**

Replace lines 23-75 with:

```markdown
## How to Query

**Step 1: Get config and repo context** (run once):

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
[ -f ".context-hub.conf" ] && source ".context-hub.conf"

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Step 2: Search Graphiti** (use GROUP_ID from above):

```python
# Search nodes (entities)
nodes_result = mcp__graphiti__search_nodes({
    "query": "authentication patterns",
    "group_ids": [GROUP_ID],  # Always "main"
    "max_nodes": 10
})

# Search facts (relationships)
facts_result = mcp__graphiti__search_memory_facts({
    "query": "authentication flow",
    "group_ids": [GROUP_ID],
    "max_facts": 20
})
```
```

**Step 2: Replace "How to Save" section**

Replace lines 77-148 with:

```markdown
## How to Save

When you make a decision, discover a pattern, or user says "remember this":

**Step 1: Get context** (if not already loaded):

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Step 2: Save with repo tag**:

```python
# Format episode body with repo prefix
episode_body = f"""Repo: {REPO_NAME}

Decision: Using JWT tokens stored in httponly cookies.

Rationale:
- XSS protection via httponly flag
- CSRF protection via SameSite attribute
- Automatic token rotation on refresh

Implementation:
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Redis for token storage
"""

result = mcp__graphiti__add_memory({
    "name": "Auth Decision: JWT with httponly cookies",
    "episode_body": episode_body,
    "group_id": GROUP_ID,
    "source": "context-hub",
    "source_description": f"Saved from {REPO_NAME}"
})

episode_id = result.get('episode_id', result.get('uuid'))
```
```

**Step 3: Update Configuration section**

Replace lines 167-177 with:

```markdown
## Configuration

**Global config** (recommended): `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
```

**Local override** (optional): `.context-hub.conf` in repo

Group ID defaults to "main" for unified cross-repo knowledge graph.
```

**Step 4: Commit**

```bash
git add skills/using-graphiti-memory/SKILL.md
git commit -m "refactor: update using-graphiti-memory skill for Bash config"
```

---

## Task 9: Update exploring-knowledge-graph Skill

**Files:**
- Modify: `skills/exploring-knowledge-graph/SKILL.md`

**Step 1: Replace config loading in examples**

Find all Python config loading blocks and replace with:

```bash
[ -f "$HOME/.config/claude/graphiti-context-hub.conf" ] && source "$HOME/.config/claude/graphiti-context-hub.conf"
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Step 2: Update all MCP tool calls**

Change `group_ids: [group_id]` to `group_ids: [GROUP_ID]` throughout.

**Step 3: Commit**

```bash
git add skills/exploring-knowledge-graph/SKILL.md
git commit -m "refactor: update exploring-knowledge-graph skill for Bash config"
```

---

## Task 10: Update serena-code-architecture Skill

**Files:**
- Modify: `skills/serena-code-architecture/SKILL.md`

**Step 1: Find and replace config loading**

Search for Python YAML loading blocks and replace with Bash helper.

**Step 2: Update save patterns with repo tagging**

Find all `mcp__graphiti__add_memory` calls and update to include `Repo: {REPO_NAME}` prefix in episode_body.

**Step 3: Commit**

```bash
git add skills/serena-code-architecture/SKILL.md
git commit -m "refactor: update serena-code-architecture skill for Bash config"
```

---

## Task 11: Update README Documentation

**Files:**
- Modify: `README.md`

**Step 1: Update Configuration section**

Replace lines 16-26 with:

```markdown
## Configuration

**Global Config** (recommended): `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
```

**Local Override** (optional): `.context-hub.conf` in repo

Run `/context-hub-setup` to create global config automatically.

**Group ID**: Uses "main" for unified cross-repo knowledge graph. All memories include repo context for flexible filtering.
```

**Step 2: Add section about repo tagging**

After "How It Works" section, add:

```markdown
### Repository Tagging

All memories automatically include repository context:

```
Repo: graphiti-context-hub

Decision: Implemented user-level group_id

Rationale: Enables cross-repo pattern discovery
```

**Benefits**:
- Search by repo: "authentication in graphiti-context-hub"
- Search globally: "authentication patterns" finds across all repos
- See which projects use similar patterns
- Graphiti extracts repo names as entities automatically
```

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for user-level group_id"
```

---

## Task 12: Update context-retrieval Agent

**Files:**
- Modify: `agents/context-retrieval.md`

**Step 1: Update Graphiti query examples**

Find the config loading patterns and replace with Bash helper.

**Step 2: Add repo tagging to examples**

Show that query results will include repo context.

**Step 3: Commit**

```bash
git add agents/context-retrieval.md
git commit -m "refactor: update context-retrieval agent for Bash config"
```

---

## Task 13: Test All Commands

**Files:**
- All commands

**Step 1: Create global config**

```bash
/context-hub-setup
```

Expected: Creates `~/.config/claude/graphiti-context-hub.conf` with `GRAPHITI_GROUP_ID=main`

**Step 2: Test memory search**

```bash
/memory-search test query
```

Expected: Uses group_id="main", shows current repo

**Step 3: Test memory save**

```bash
/memory-save
```

Expected: Prompts for content, saves with `Repo: context-hub-plugin` prefix

**Step 4: Test memory list**

```bash
/memory-list 5
```

Expected: Lists recent episodes from group "main"

**Step 5: Verify repo tagging**

Search for a saved memory - episode body should start with `Repo: {repo_name}`

**Step 6: Commit**

```bash
git add -A
git commit -m "test: verify all commands work with new config system"
```

---

## Final Checklist

- [ ] Global config file format created
- [ ] All commands use Bash config loading
- [ ] All commands include repo in episode bodies
- [ ] All skills updated with Bash helper
- [ ] README documentation updated
- [ ] `/context-hub-setup` creates global config
- [ ] All MCP calls use `group_id="main"`
- [ ] Repo tagging works in saved episodes
- [ ] Old YAML config still works (backward compatible)
- [ ] Commands tested end-to-end

---

## Success Criteria

- ✅ Global config in `~/.config/claude/graphiti-context-hub.conf`
- ✅ `group_id="main"` used for all operations
- ✅ All episodes include `Repo: {repo_name}` prefix
- ✅ Bash config loading works (no Python yaml dependency)
- ✅ Can search by repo or across all repos
- ✅ Graphiti extracts repo names as entities
- ✅ Local override still works via `.context-hub.conf`
- ✅ All commands and skills updated
- ✅ Documentation complete
