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
