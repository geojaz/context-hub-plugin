# Graphiti Context Hub Simplification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor context-hub-plugin into graphiti-context-hub by removing all adapter abstraction layers and Forgetful support, using Graphiti MCP tools directly with simplified YAML config.

**Architecture:** Commands read `.context-hub.yaml` directly, detect group_id inline, and call `mcp__graphiti__*` tools. No Python library abstraction needed.

**Tech Stack:** Claude Code plugin system, Graphiti MCP, YAML config, inline Python in markdown commands

---

## Task 1: Rename Plugin and Update Metadata

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`

**Step 1: Update plugin.json with new name**

```json
{
  "name": "graphiti-context-hub",
  "description": "Context retrieval using Graphiti knowledge graph, Context7 docs, and Serena symbol analysis",
  "version": "3.0.0",
  "author": {
    "name": "Eric Hole",
    "url": "https://github.com/geojaz"
  },
  "license": "MIT",
  "repository": "https://github.com/geojaz/graphiti-context-hub"
}
```

**Step 2: Update marketplace.json**

```json
{
  "marketplace_id": "geojaz-graphiti-context-hub",
  "marketplace_url": "https://github.com/geojaz/graphiti-context-hub"
}
```

**Step 3: Commit metadata changes**

```bash
git add .claude-plugin/
git commit -m "refactor: rename plugin to graphiti-context-hub"
```

---

## Task 2: Update Config File Format

**Files:**
- Modify: `.context-hub.yaml`
- Create: `.context-hub.yaml.example`

**Step 1: Update config to Graphiti-only format**

Edit `.context-hub.yaml`:
```yaml
graphiti:
  group_id: "auto"  # auto-detect from git repo, or set explicit name
  endpoint: "http://localhost:8000"  # optional, defaults to localhost:8000
```

**Step 2: Create example config**

Create `.context-hub.yaml.example`:
```yaml
# Graphiti Context Hub Configuration

graphiti:
  # Group ID for isolating this project's knowledge graph
  # "auto" = detect from git repository name
  # Or set explicit: "my-project-name"
  group_id: "auto"

  # Graphiti MCP endpoint (optional)
  # Default: http://localhost:8000
  # endpoint: "http://localhost:8000"
```

**Step 3: Commit config changes**

```bash
git add .context-hub.yaml .context-hub.yaml.example
git commit -m "refactor: simplify config to Graphiti-only format"
```

---

## Task 3: Delete Adapter Layer and Forgetful Code

**Files:**
- Delete: `lib/` (entire directory)
- Delete: `examples/` (entire directory)
- Delete: `README-lib.md`
- Delete: `skills/curating-memories/` (Forgetful-specific)
- Delete: `skills/using-memory-adapter/` (adapter-specific)

**Step 1: Remove Python library code**

```bash
rm -rf lib/
rm -rf examples/
rm README-lib.md
```

**Step 2: Remove Forgetful-specific skills**

```bash
rm -rf skills/curating-memories/
rm -rf skills/using-memory-adapter/
```

**Step 3: Commit deletions**

```bash
git add -A
git commit -m "refactor: remove adapter layer and Forgetful support"
```

---

## Task 4: Update /memory-search Command

**Files:**
- Modify: `commands/memory-search.md`

**Step 1: Rewrite command with direct MCP calls**

Replace entire content of `commands/memory-search.md`:

```markdown
---
description: Search Graphiti knowledge graph semantically
---

# Memory Search

Search the knowledge graph for relevant memories using Graphiti.

## Your Task

Search Graphiti for: **$ARGUMENTS**

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id if set to auto
if group_id_setting == 'auto':
    # Try to get from git repo name
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            # Extract repo name from URL
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Using group_id: {group_id}\n")
```

**Step 2: Search Graphiti**

```python
query = "$ARGUMENTS"

# Call Graphiti MCP tool directly
result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [group_id],
    "max_nodes": 10
})

# Display results
nodes = result.get('nodes', [])
print(f"Found {len(nodes)} memories:\n")

for i, node in enumerate(nodes, 1):
    name = node.get('name', 'Untitled')
    summary = node.get('summary', '')
    created = node.get('created_at', '')[:10]

    print(f"{i}. {name}")
    if summary:
        print(f"   {summary[:150]}...")
    print(f"   Created: {created}")
    print()
```

## Response Format

Present results clearly with:
1. Group ID being searched
2. Number of results found
3. For each memory: title, summary snippet, creation date
4. Suggestions to refine search if needed
```

**Step 2: Test the updated command**

Run: `/memory-search authentication patterns`
Expected: Results from Graphiti with detected group_id

**Step 3: Commit**

```bash
git add commands/memory-search.md
git commit -m "refactor: update memory-search to use Graphiti MCP directly"
```

---

## Task 5: Update /memory-save Command

**Files:**
- Modify: `commands/memory-save.md`

**Step 1: Rewrite command with direct MCP calls**

Replace entire content of `commands/memory-save.md`:

```markdown
---
description: Save current context to Graphiti knowledge graph
---

# Memory Save

Save current context as an episode in the Graphiti knowledge graph.

## Your Task

Save the current conversation context as a memory.

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id if set to auto
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Using group_id: {group_id}\n")
```

**Step 2: Ask user what to save**

Use AskUserQuestion to gather:
- Title/name for this memory
- Content to save (summary of current work/decision)
- Any additional context

**Step 3: Save to Graphiti**

```python
# Save episode
result = mcp__graphiti__add_memory({
    "name": title_from_user,
    "episode_body": content_from_user,
    "group_id": group_id,
    "source": "context-hub",
    "source_description": "Saved via graphiti-context-hub plugin"
})

episode_id = result.get('episode_id', result.get('uuid', 'unknown'))
print(f"✓ Saved memory with ID: {episode_id}")
```

## Response Format

1. Confirm what was saved
2. Show the episode ID
3. Suggest next actions (search for it, explore related memories)
```

**Step 2: Commit**

```bash
git add commands/memory-save.md
git commit -m "refactor: update memory-save to use Graphiti MCP directly"
```

---

## Task 6: Update /memory-list Command

**Files:**
- Modify: `commands/memory-list.md`

**Step 1: Rewrite command with direct MCP calls**

Replace entire content of `commands/memory-list.md`:

```markdown
---
description: List recent episodes from Graphiti knowledge graph
---

# Memory List

List recent episodes from the Graphiti knowledge graph.

## Your Task

List recent memories. Optional: **$ARGUMENTS** (count, default: 20)

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Using group_id: {group_id}\n")
```

**Step 2: Get episode count from arguments**

```python
args = "$ARGUMENTS".strip()
limit = int(args) if args.isdigit() else 20
```

**Step 3: List episodes**

```python
# Call Graphiti MCP tool
result = mcp__graphiti__get_episodes({
    "group_ids": [group_id],
    "max_episodes": limit
})

episodes = result.get('episodes', [])
print(f"Recent {len(episodes)} episodes:\n")

for i, ep in enumerate(episodes, 1):
    name = ep.get('name', 'Untitled')
    content = ep.get('content', '')
    created = ep.get('created_at', '')[:10]

    print(f"{i}. {name}")
    print(f"   {content[:100]}...")
    print(f"   Created: {created}")
    print()
```

## Response Format

List episodes with:
1. Episode name
2. Content preview (100 chars)
3. Creation date
```

**Step 2: Commit**

```bash
git add commands/memory-list.md
git commit -m "refactor: update memory-list to use Graphiti MCP directly"
```

---

## Task 7: Update /memory-explore Command

**Files:**
- Modify: `commands/memory-explore.md`

**Step 1: Rewrite command with direct MCP calls**

Replace entire content of `commands/memory-explore.md`:

```markdown
---
description: Deep exploration of Graphiti knowledge graph
---

# Memory Explore

Explore the Graphiti knowledge graph from a starting query.

## Your Task

Explore starting from: **$ARGUMENTS**

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Using group_id: {group_id}\n")
```

**Step 2: Search nodes and facts**

```python
query = "$ARGUMENTS"

# Get nodes
nodes_result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [group_id],
    "max_nodes": 10
})

# Get facts/relationships
facts_result = mcp__graphiti__search_memory_facts({
    "query": query,
    "group_ids": [group_id],
    "max_facts": 20
})

nodes = nodes_result.get('nodes', [])
facts = facts_result.get('facts', [])

print(f"Found {len(nodes)} nodes and {len(facts)} relationships:\n")
print("## Nodes\n")
for node in nodes:
    print(f"- {node.get('name', 'Untitled')}: {node.get('summary', '')[:80]}")

print("\n## Relationships\n")
for fact in facts:
    print(f"- {fact.get('fact', 'Unknown relationship')}")
```

## Response Format

Present:
1. Nodes found (entities)
2. Relationships/facts discovered
3. Suggested next exploration steps
```

**Step 2: Commit**

```bash
git add commands/memory-explore.md
git commit -m "refactor: update memory-explore to use Graphiti MCP directly"
```

---

## Task 8: Update /context_gather Command

**Files:**
- Modify: `commands/context_gather.md`

**Step 1: Simplify command to launch agent**

Replace entire content of `commands/context_gather.md`:

```markdown
---
description: Gather comprehensive context from Graphiti, code, and docs
---

# Context Gather

Launch the context-retrieval agent to gather context from multiple sources.

**Task**: $ARGUMENTS

## Implementation

Launch the context-retrieval agent with the task description. The agent will:
1. Query Graphiti knowledge graph for relevant memories
2. Read linked code artifacts and files
3. Query Context7 for framework documentation
4. Search web if needed

The agent uses Graphiti MCP tools directly.
```

**Step 2: Commit**

```bash
git add commands/context_gather.md
git commit -m "refactor: simplify context_gather command"
```

---

## Task 9: Update /context-hub-setup Command

**Files:**
- Modify: `commands/context-hub-setup.md`

**Step 1: Rewrite setup command**

Replace entire content of `commands/context-hub-setup.md`:

```markdown
---
description: Configure Graphiti Context Hub and verify setup
---

# Context Hub Setup

Configure Graphiti Context Hub and verify all prerequisites.

## Your Task

Set up and verify Graphiti Context Hub configuration.

## Implementation

**Step 1: Check prerequisites**

```python
import subprocess
from pathlib import Path

print("Checking prerequisites...\n")

# Check if Serena is installed
try:
    result = subprocess.run(['claude', 'plugins', 'list'], capture_output=True, text=True)
    has_serena = 'serena' in result.stdout.lower()
    print(f"✓ Serena plugin: {'installed' if has_serena else 'NOT FOUND'}")
except:
    print("⚠ Could not check Serena plugin")
    has_serena = False

# Check if Context7 is installed
try:
    result = subprocess.run(['claude', 'plugins', 'list'], capture_output=True, text=True)
    has_context7 = 'context7' in result.stdout.lower()
    print(f"✓ Context7 plugin: {'installed' if has_context7 else 'NOT FOUND (recommended)'}")
except:
    print("⚠ Could not check Context7 plugin")
    has_context7 = False

print()
```

**Step 2: Check or create config file**

```python
import yaml

config_path = Path.cwd() / '.context-hub.yaml'

if config_path.exists():
    print("✓ Config file exists")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    print(f"  group_id: {config.get('graphiti', {}).get('group_id', 'NOT SET')}")
    print(f"  endpoint: {config.get('graphiti', {}).get('endpoint', 'default')}")
else:
    print("Creating default config file...")
    default_config = {
        'graphiti': {
            'group_id': 'auto',
            'endpoint': 'http://localhost:8000'
        }
    }
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    print("✓ Created .context-hub.yaml")

print()
```

**Step 3: Test Graphiti connection**

```python
# Detect group_id
config_path = Path.cwd() / '.context-hub.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Detected group_id: {group_id}")

# Test Graphiti connection
try:
    result = mcp__graphiti__get_status({})
    print("✓ Graphiti MCP connection successful")
    print(f"  Status: {result}")
except Exception as e:
    print(f"✗ Graphiti MCP connection failed: {e}")

print()
```

**Step 4: Show summary**

```python
print("Setup Summary:")
print(f"- Serena: {'✓' if has_serena else '✗ Install with: claude plugins install serena'}")
print(f"- Context7: {'✓' if has_context7 else 'ℹ Recommended: claude plugins install context7 --marketplace pleaseai/claude-code-plugins'}")
print(f"- Config: ✓ .context-hub.yaml")
print(f"- Group ID: {group_id}")
print(f"- Graphiti: Test connection above")
```

## Response Format

Show:
1. Prerequisites status (Serena, Context7)
2. Config file status
3. Detected group_id
4. Graphiti connection test result
5. Next steps if anything is missing
```

**Step 2: Commit**

```bash
git add commands/context-hub-setup.md
git commit -m "refactor: update context-hub-setup for Graphiti-only"
```

---

## Task 10: Update /encode-repo-serena Command

**Files:**
- Modify: `commands/encode-repo-serena.md`

**Step 1: Update to use Graphiti MCP directly**

Replace entire content of `commands/encode-repo-serena.md`:

```markdown
---
description: Encode repository into Graphiti using Serena symbol analysis
---

# Encode Repository with Serena

Bootstrap repository into Graphiti knowledge graph using Serena's symbol analysis.

## Your Task

Encode the current repository into Graphiti using symbol-level analysis.

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

print(f"Using group_id: {group_id}\n")
```

**Step 2: Use Serena to get repository overview**

Use Serena MCP tools to get symbol overview for key files:

```python
# Find main source files (adjust pattern for language)
import glob

source_files = glob.glob('**/*.py', recursive=True)
source_files = [f for f in source_files if not f.startswith('.') and 'venv' not in f]

print(f"Found {len(source_files)} source files")
print("Getting symbol overview from Serena...")
```

**Step 3: Extract and save architecture to Graphiti**

For each significant file:
1. Use `mcp__plugin_serena_serena__get_symbols_overview` to get symbols
2. Create episodes in Graphiti with architectural insights

```python
episodes_created = 0

for file_path in source_files[:10]:  # Limit to avoid overwhelming
    try:
        # Get symbols from Serena
        symbols = mcp__plugin_serena_serena__get_symbols_overview({
            "relative_path": file_path,
            "depth": 1
        })

        # Create episode with symbol information
        episode_content = f"File: {file_path}\n\nSymbols:\n{symbols}"

        result = mcp__graphiti__add_memory({
            "name": f"Architecture: {file_path}",
            "episode_body": episode_content,
            "group_id": group_id,
            "source": "serena-encode",
            "source_description": f"Automated repository encoding via Serena"
        })

        episodes_created += 1
        print(f"✓ Encoded {file_path}")
    except Exception as e:
        print(f"⚠ Skipped {file_path}: {e}")

print(f"\n✓ Created {episodes_created} architecture episodes in Graphiti")
```

## Response Format

1. Number of files analyzed
2. Symbols extracted per file
3. Episodes created in Graphiti
4. Suggestions for next steps (search for specific symbols, explore graph)
```

**Step 2: Commit**

```bash
git add commands/encode-repo-serena.md
git commit -m "refactor: update encode-repo-serena to use Graphiti MCP directly"
```

---

## Task 11: Update context-retrieval Agent

**Files:**
- Modify: `agents/context-retrieval.md`

**Step 1: Update agent to use Graphiti MCP directly**

Replace the "Memory Backend" section (lines 16-39) with:

```markdown
### 1. Graphiti Knowledge Graph (Primary Source)

**Query the knowledge graph** using Graphiti MCP tools:

```python
import yaml
from pathlib import Path
import subprocess

# Load config and detect group_id
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

# Search nodes
nodes_result = mcp__graphiti__search_nodes({
    "query": "<your search query>",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Search facts/relationships
facts_result = mcp__graphiti__search_memory_facts({
    "query": "<your search query>",
    "group_ids": [group_id],
    "max_facts": 20
})
```

**Tips:**
- Nodes are entities (classes, functions, concepts)
- Facts are relationships between entities
- Use both to build complete understanding
```

**Step 2: Remove Dynamic Discovery section (lines 59-71)**

Delete the entire "Dynamic Discovery" section as it's no longer needed.

**Step 3: Update example workflows (lines 174-202)**

Replace with direct MCP tool usage:

```markdown
**Task**: "Implement OAuth2 for FastAPI MCP server"

**Your Process**:
1. Query Graphiti:
```python
# Direct MCP tool call with auto-detected group_id
nodes_result = mcp__graphiti__search_nodes({
    "query": "OAuth FastAPI MCP JWT authentication",
    "group_ids": [group_id],
    "max_nodes": 10
})

facts_result = mcp__graphiti__search_memory_facts({
    "query": "OAuth authentication flow",
    "group_ids": [group_id],
    "max_facts": 20
})
```
2. Read linked code files mentioned in node metadata
3. Query Context7: "fastapi oauth2 jwt"
4. Return: OAuth patterns + code snippets + FastAPI Context7 guidance

**Task**: "Add PostgreSQL RLS for multi-tenant"

**Your Process**:
1. Query Graphiti:
```python
nodes_result = mcp__graphiti__search_nodes({
    "query": "PostgreSQL multi-tenant RLS row level security",
    "group_ids": [group_id],
    "max_nodes": 10
})
```
2. Read any linked SQL migration files
3. Query Context7: "postgresql row level security"
4. Return: RLS patterns + migration strategy + PostgreSQL docs
```

**Step 4: Commit**

```bash
git add agents/context-retrieval.md
git commit -m "refactor: update context-retrieval agent for Graphiti MCP"
```

---

## Task 12: Create New Skill: using-graphiti-memory

**Files:**
- Create: `skills/using-graphiti-memory/SKILL.md`

**Step 1: Create new Graphiti-focused skill**

Create `skills/using-graphiti-memory/SKILL.md`:

```markdown
---
name: using-graphiti-memory
description: When to query and save to Graphiti knowledge graph. PROACTIVELY query before starting work. Save important decisions and patterns.
allowed-tools: Read, Glob, Grep
---

# Using Graphiti Memory

## When to Use

**Query PROACTIVELY:**
- ✅ Before implementing ANY feature
- ✅ When user mentions past work or patterns
- ✅ When architecting new components
- ✅ Before making technical decisions

**Save Immediately After:**
- ✅ Making architectural decisions
- ✅ Discovering reusable patterns
- ✅ Learning from bugs/issues
- ✅ Receiving user preferences

## How to Query

```python
import yaml
from pathlib import Path
import subprocess

# Load config and detect group_id
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Auto-detect group_id if needed
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

# Search nodes (entities)
nodes_result = mcp__graphiti__search_nodes({
    "query": "authentication patterns",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Search facts (relationships)
facts_result = mcp__graphiti__search_memory_facts({
    "query": "authentication flow",
    "group_ids": [group_id],
    "max_facts": 20
})
```

## How to Save

```python
# Save an episode (Graphiti automatically extracts entities)
result = mcp__graphiti__add_memory({
    "name": "Auth Decision: JWT with httponly cookies",
    "episode_body": """
    Decision: Using JWT tokens stored in httponly cookies.

    Rationale:
    - XSS protection via httponly flag
    - CSRF protection via SameSite attribute
    - Automatic token rotation on refresh

    Implementation:
    - Access token: 15 min expiry
    - Refresh token: 7 day expiry
    - Redis for token storage
    """,
    "group_id": group_id,
    "source": "context-hub",
    "source_description": "Architectural decision"
})

episode_id = result.get('episode_id', result.get('uuid'))
```

## Graphiti Features

**Automatic Entity Extraction:**
- Graphiti extracts entities (JWT, Redis, tokens) automatically
- Creates relationships between entities
- No manual linking required

**Search Capabilities:**
- Semantic search across nodes (entities)
- Relationship search via facts
- Temporal queries (what changed when)

**Knowledge Graph Benefits:**
- See connections between decisions
- Trace architectural evolution
- Discover related patterns across projects

## Configuration

Set group_id in `.context-hub.yaml`:

```yaml
graphiti:
  group_id: "auto"  # or explicit: "my-project"
  endpoint: "http://localhost:8000"  # optional
```

Group ID is auto-detected from git repository name when set to "auto".

## Common Patterns

**Before implementing a feature:**
```python
# Search for related patterns
nodes = mcp__graphiti__search_nodes({
    "query": f"implementing {feature_name}",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Check for architectural decisions
facts = mcp__graphiti__search_memory_facts({
    "query": f"{feature_name} architecture",
    "group_ids": [group_id],
    "max_facts": 20
})
```

**After making a decision:**
```python
mcp__graphiti__add_memory({
    "name": f"Decision: {decision_title}",
    "episode_body": f"""
    Decision: {what_you_decided}

    Context: {why_this_matters}

    Rationale: {reasoning}

    Trade-offs: {alternatives_considered}
    """,
    "group_id": group_id,
    "source": "context-hub"
})
```
```

**Step 2: Commit**

```bash
git add skills/using-graphiti-memory/
git commit -m "feat: add using-graphiti-memory skill"
```

---

## Task 13: Update exploring-knowledge-graph Skill

**Files:**
- Modify: `skills/exploring-knowledge-graph/SKILL.md`

**Step 1: Update skill for Graphiti MCP**

Replace Forgetful-specific content with Graphiti graph exploration:

```markdown
---
name: exploring-knowledge-graph
description: Deep exploration of Graphiti knowledge graph. Use when investigating connections, tracing decisions, or understanding architectural evolution.
allowed-tools: Read, Glob, Grep
---

# Exploring the Knowledge Graph

## When to Use

**Deep graph exploration:**
- ✅ Tracing how a decision evolved over time
- ✅ Understanding connections between components
- ✅ Finding related architectural patterns
- ✅ Investigating why something was built a certain way

## Exploration Strategy

**Step 1: Find starting point**

```python
import yaml
from pathlib import Path
import subprocess

# Load config and detect group_id (standard pattern)
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

# Find starting nodes
starting_nodes = mcp__graphiti__search_nodes({
    "query": "authentication architecture",
    "group_ids": [group_id],
    "max_nodes": 5
})
```

**Step 2: Explore relationships**

```python
# Get facts related to the topic
facts = mcp__graphiti__search_memory_facts({
    "query": "authentication dependencies relationships",
    "group_ids": [group_id],
    "max_facts": 30
})

# Analyze fact patterns
for fact in facts.get('facts', []):
    print(f"Relationship: {fact.get('fact')}")
    print(f"  From: {fact.get('source_node_uuid')}")
    print(f"  To: {fact.get('target_node_uuid')}")
```

**Step 3: Get episode context**

```python
# Get episodes (chronological context)
episodes = mcp__graphiti__get_episodes({
    "group_ids": [group_id],
    "max_episodes": 20
})

# Look for evolution over time
for ep in episodes.get('episodes', []):
    if 'authentication' in ep.get('name', '').lower():
        print(f"{ep.get('created_at')}: {ep.get('name')}")
```

## Exploration Patterns

**Pattern 1: Trace a decision's evolution**

1. Search nodes for the concept
2. Get facts showing relationships
3. Get episodes chronologically
4. Identify what changed and why

**Pattern 2: Understand component dependencies**

1. Search for component name
2. Get facts showing dependencies
3. Map the dependency graph
4. Identify potential issues

**Pattern 3: Find reusable patterns**

1. Search broadly (e.g., "API design patterns")
2. Group nodes by similarity
3. Extract common patterns from facts
4. Synthesize reusable approach

## Response Format

Present findings as:

```markdown
## Exploration: [Topic]

### Central Entities
- Entity 1: Description
- Entity 2: Description

### Key Relationships
- Entity A → Entity B: Relationship type
- Entity B → Entity C: Relationship type

### Evolution Timeline
- [Date]: Initial decision
- [Date]: Refinement
- [Date]: Current state

### Insights
- Pattern discovered
- Dependency identified
- Trade-off understood
```

## Anti-Patterns

❌ Exploring without a clear starting query
❌ Looking only at nodes without checking facts
❌ Ignoring temporal context (episode chronology)
❌ Not synthesizing findings into actionable insights
```

**Step 2: Commit**

```bash
git add skills/exploring-knowledge-graph/
git commit -m "refactor: update exploring-knowledge-graph for Graphiti"
```

---

## Task 14: Update serena-code-architecture Skill

**Files:**
- Modify: `skills/serena-code-architecture/SKILL.md`

**Step 1: Update to use Graphiti MCP directly**

Find and replace the memory-saving sections to use `mcp__graphiti__add_memory` instead of adapter:

Replace memory save pattern (around lines 80-120) with:

```python
# Load config and detect group_id
import yaml
from pathlib import Path
import subprocess

config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

# Save architectural finding to Graphiti
result = mcp__graphiti__add_memory({
    "name": f"Architecture: {component_name}",
    "episode_body": architecture_description,
    "group_id": group_id,
    "source": "serena-analysis",
    "source_description": f"Code architecture analysis via Serena"
})
```

**Step 2: Commit**

```bash
git add skills/serena-code-architecture/
git commit -m "refactor: update serena-code-architecture for Graphiti MCP"
```

---

## Task 15: Update README

**Files:**
- Modify: `README.md`

**Step 1: Update README for Graphiti-only plugin**

Replace entire content of `README.md`:

```markdown
# Graphiti Context Hub

Unified context retrieval for Claude Code - orchestrates **Graphiti knowledge graph**, **Context7 documentation**, and **Serena symbol analysis** into a single context-gathering workflow.

## Installation

```bash
claude plugins install graphiti-context-hub --marketplace geojaz
```

Or install from local path:
```bash
claude plugins install /path/to/graphiti-context-hub
```

## Configuration

Create `.context-hub.yaml`:

```yaml
graphiti:
  group_id: "auto"  # auto-detect from git repo, or set explicit name
  endpoint: "http://localhost:8000"  # optional, defaults to localhost:8000
```

**Group ID**: Isolates this project's knowledge graph. Set to `"auto"` to auto-detect from git repository name, or set explicit name like `"my-project"`.

## Prerequisites

### Required: Graphiti MCP Server

Start Graphiti MCP server:
```bash
# Follow Graphiti MCP installation instructions
graphiti-server start
```

### Required: Serena (for `/encode-repo-serena`)
```bash
claude plugins install serena
```

### Recommended: Context7 (for framework docs)
```bash
claude plugins install context7 --marketplace pleaseai/claude-code-plugins
```

## Setup

Run the setup command to configure and verify:

```bash
/context-hub-setup
```

This will:
1. Check if Serena and Context7 plugins are installed
2. Create `.context-hub.yaml` configuration file
3. Test Graphiti MCP connectivity
4. Verify group_id auto-detection

## Commands

### Context Retrieval

| Command | Description |
|---------|-------------|
| `/context_gather <task>` | Gather context from Graphiti, code, and docs |
| `/encode-repo-serena` | Bootstrap repository into Graphiti using Serena |

### Memory Management

| Command | Description |
|---------|-------------|
| `/memory-search <query>` | Search knowledge graph semantically |
| `/memory-list [count]` | List recent episodes |
| `/memory-save` | Save current context as episode |
| `/memory-explore <query>` | Deep knowledge graph traversal |

### Setup

| Command | Description |
|---------|-------------|
| `/context-hub-setup` | Configure and verify setup |

## Skills

Graphiti Context Hub includes auto-discovered skills:

### Memory Skills
| Skill | Description |
|-------|-------------|
| `using-graphiti-memory` | When/how to query and save to Graphiti |
| `exploring-knowledge-graph` | Deep graph traversal and relationship discovery |

### Serena Skills
| Skill | Description |
|-------|-------------|
| `using-serena-symbols` | Symbol-level code analysis guidance |
| `serena-code-architecture` | Architectural analysis with Graphiti integration |

## How It Works

### /context_gather

Orchestrates multiple sources:

1. **Graphiti Knowledge Graph** - Semantic search across entities and relationships
2. **File System** - Read actual code files
3. **Context7** - Framework-specific documentation (if installed)
4. **Serena** - Symbol-level code analysis (if installed)
5. **WebSearch** - Fallback for recent information

Returns synthesized summary with:
- Relevant entities and relationships
- Code patterns and snippets
- Framework guidance
- Architectural decisions

### /encode-repo-serena

Uses Serena's LSP-powered analysis:
- **Symbol extraction** - Classes, functions, methods with locations
- **Relationship discovery** - Dependencies and references
- **Cross-file analysis** - Component connections

Stores findings as episodes in Graphiti for future retrieval.

## Example Usage

```bash
# Before implementing a feature
/context_gather implement OAuth2 authentication for the API

# Bootstrap a new project
/encode-repo-serena

# Quick memory search
/memory-search authentication patterns

# Save an important decision
/memory-save

# Explore the knowledge graph
/memory-explore authentication architecture
```

## Architecture

```
graphiti-context-hub
├── skills/
│   ├── using-graphiti-memory/      ─── Memory usage guide
│   ├── exploring-knowledge-graph/   ─── Graph traversal
│   ├── using-serena-symbols/        ─── Symbol analysis
│   └── serena-code-architecture/    ─── Architecture workflows
├── commands/
│   ├── context_gather.md            ─── Multi-source retrieval
│   ├── encode-repo-serena.md        ─── Repository encoding
│   └── memory-*.md                  ─── Memory management
└── agents/
    └── context-retrieval.md         ─── Context gathering agent
```

## Graphiti Features

**Automatic Entity Extraction:**
- Saves episodes and automatically extracts entities
- Creates relationships between entities
- No manual linking required

**Knowledge Graph:**
- Entities: Classes, functions, concepts, decisions
- Relationships: Dependencies, implementations, influences
- Temporal: Track evolution over time

**Search:**
- Semantic search across nodes (entities)
- Relationship search via facts
- Episode chronology for context

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README for Graphiti-only plugin"
```

---

## Task 16: Clean Up Old Documentation

**Files:**
- Delete: `docs/MIGRATION.md`
- Delete: `docs/plans/2026-02-06-*` (old design docs)

**Step 1: Remove obsolete documentation**

```bash
rm docs/MIGRATION.md
rm docs/plans/2026-02-06-pluggable-memory-backend-design.md
rm docs/plans/2026-02-06-pluggable-memory-backend-implementation.md
rm docs/plans/2026-02-06-phase2-mcp-integration.md
```

**Step 2: Commit**

```bash
git add -A
git commit -m "docs: remove obsolete adapter documentation"
```

---

## Task 17: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

**Step 1: Update agent description**

Replace content to reflect Graphiti-only:

```markdown
# Agents

## context-retrieval

Context retrieval specialist for gathering relevant context before planning or implementation.

**Sources:**
1. **Graphiti Knowledge Graph** - Semantic search across entities and relationships
2. **File System** - Read actual code referenced in memories
3. **Context7** - Framework-specific documentation
4. **WebSearch** - Fallback for recent information

**Usage:**
- Launched by `/context_gather` command
- Uses Graphiti MCP tools directly
- Auto-detects group_id from config
- Returns synthesized context summary

**Tools:**
- Graphiti MCP: `search_nodes`, `search_memory_facts`, `get_episodes`
- Context7: `resolve-library-id`, `get-library-docs`
- Core: Read, Glob, Grep, WebSearch, WebFetch
```

**Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md for Graphiti-only"
```

---

## Task 18: Final Verification and Testing

**Files:**
- All updated commands and skills

**Step 1: Test each command**

Run each command to verify it works:

```bash
# Test setup
/context-hub-setup

# Test memory operations
/memory-list 5
/memory-search "test query"
/memory-save

# Test context gathering
/context_gather "test task"
```

**Step 2: Verify group_id detection**

Check that group_id is correctly detected:
- From git remote URL
- Falls back to directory name

**Step 3: Create summary commit**

```bash
git add -A
git commit -m "refactor: complete Graphiti-only simplification

- Removed adapter layer (lib/, backends/)
- Removed Forgetful support
- Commands use Graphiti MCP tools directly
- Simplified config to graphiti-only
- Updated all skills and documentation
- Plugin renamed to graphiti-context-hub"
```

---

## Final Checklist

✅ Plugin renamed to `graphiti-context-hub`
✅ Config simplified to Graphiti-only format
✅ All adapter code removed (lib/, examples/)
✅ All Forgetful code removed (skills, backend)
✅ All commands updated to use MCP tools directly
✅ All skills updated for Graphiti
✅ README updated
✅ Documentation cleaned up
✅ Group ID detection working
✅ All commands tested

---

## Success Criteria

- ✅ Plugin renamed and version bumped to 3.0.0
- ✅ No Python library code (removed lib/, examples/)
- ✅ Commands use inline group_id detection
- ✅ All Graphiti MCP calls work correctly
- ✅ Group ID auto-detection prevents cross-contamination
- ✅ Skills guide Claude to use Graphiti effectively
- ✅ Documentation is accurate and complete
