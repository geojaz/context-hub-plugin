---
description: Configure Graphiti MCP backend and plugin prerequisites
---

# Context Hub Setup

Configure Context Hub with Graphiti memory backend and verify prerequisites.

## Overview

This setup command will:
1. Check plugin prerequisites (Serena, Context7)
2. Verify Graphiti MCP configuration
3. Create `.context-hub.yaml` configuration file
4. Test Graphiti connectivity
5. Verify group_id auto-detection

## Step 1: Check Plugin Prerequisites

Check if required plugins are installed:

```bash
claude plugins list
```

Look for:
- `serena` or similar (for code analysis)
- `context7` or similar (for framework docs)

**If Serena is not installed:**
```
To use /encode-repo-serena, install the Serena plugin:

  claude plugins install serena

Or search for it in the marketplace:

  claude plugins search serena
```

**If Context7 is not installed:**
```
For framework documentation in /context_gather, install Context7:

  claude plugins install context7 --marketplace pleaseai/claude-code-plugins

Or search for it:

  claude plugins search context7
```

## Step 2: Verify Graphiti MCP Configuration

Check if Graphiti MCP is configured:

```bash
claude mcp list | grep -i graphiti
```

**If not configured, guide setup:**
```
To use Graphiti, you need the Graphiti MCP server running.

Installation options:

1. Local server (Docker):
   docker run -p 8000:8000 graphiti/mcp-server

2. Remote server:
   Ensure server is accessible at configured endpoint

3. Add to Claude MCP config:
   claude mcp add graphiti --scope user -- npx @graphiti/mcp-server

For detailed setup: https://github.com/getzep/graphiti
```

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

## Step 5: Test Graphiti Connection

Verify connectivity using MCP tools:

```python
# Test Graphiti connection
try:
    result = mcp__graphiti__get_status()
    print("✅ Graphiti MCP server is connected")
    print(f"Status: {result}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Ensure Graphiti MCP server is running and configured correctly")
```

## Step 6: Verify Complete Setup

Report comprehensive status:

```python
import subprocess
from pathlib import Path

print("=" * 50)
print("Context Hub Setup Status")
print("=" * 50)
print(f"Memory Backend: graphiti")
print(f"Global Config:  ~/.config/claude/graphiti-context-hub.conf")
print(f"Local Config:   .context-hub.conf (optional)")
print()

# Check MCP status
def check_mcp(name):
    try:
        result = subprocess.run(
            ['claude', 'mcp', 'list'],
            capture_output=True,
            text=True
        )
        return name.lower() in result.stdout.lower()
    except:
        return False

mcp_status = "✅ Configured" if check_mcp("graphiti") else "❌ Not configured"
print(f"Graphiti MCP: {mcp_status}")

# Check plugins
def check_plugin(name):
    try:
        result = subprocess.run(
            ['claude', 'plugins', 'list'],
            capture_output=True,
            text=True
        )
        return name.lower() in result.stdout.lower()
    except:
        return False

serena_status = "✅ Installed" if check_plugin("serena") else "❌ Not installed"
context7_status = "✅ Installed" if check_plugin("context7") else "⚠️  Not installed (optional)"

print(f"Serena Plugin:   {serena_status}")
print(f"Context7 Plugin: {context7_status}")
print()

print("Available Commands:")
print("  /context_gather <task>  - Multi-source context retrieval")
print("  /encode-repo-serena     - Repository encoding (requires Serena)")
print("  /memory-search <query>  - Search memories")
print("  /memory-list [count]    - List recent memories")
print("  /memory-save            - Save current context")
print("  /memory-explore <query> - Knowledge graph traversal")
print("=" * 50)
```

## Step 7: Quick Test (Optional)

Test the setup:

```python
# Test Graphiti connection
result = mcp__graphiti__get_status()
print(f"✅ Graphiti status: {result}")

# List recent episodes
episodes = mcp__graphiti__get_episodes({"max_episodes": 5})
print(f"✅ Recent episodes: {len(episodes)} found")
```

**Test Serena (if installed):**
```python
# Quick Serena test
mcp__plugin_serena_serena__get_current_config()
```

**Test Context7 (if installed):**
```
Ask about a framework: "How does FastAPI dependency injection work?"
```

## Troubleshooting

### Graphiti Issues

**Connection failed:**
- Verify server is running: `curl http://localhost:8000/health`
- Check MCP config: `claude mcp list`
- Review Claude Code logs for MCP errors
- Verify Graphiti MCP server is properly configured

**MCP not found:**
```bash
claude mcp add graphiti --scope user -- npx @graphiti/mcp-server
```

### Plugin Issues

**Serena not found:**
```bash
claude plugins install serena
```

**Context7 not found:**
```bash
claude plugins install context7 --marketplace pleaseai/claude-code-plugins
```

### Configuration Issues

**Config file not found:**
- Global config should be at `~/.config/claude/graphiti-context-hub.conf`
- Run this command again to create it
- Check file permissions

**Group ID not detected:**
- Verify git repository exists: `git remote -v`
- Override by creating `.context-hub.conf` with `GRAPHITI_GROUP_ID=your-project-name`

## Configuration Reference

### Global Config
Location: `~/.config/claude/graphiti-context-hub.conf`

```bash
# Graphiti Context Hub Configuration
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
```

### Local Config (Optional)
Location: `.context-hub.conf` (project root)

```bash
# Override global settings for this project
GRAPHITI_GROUP_ID=my-project
GRAPHITI_ENDPOINT=http://localhost:8000
```

## Notes

- Configuration priority: local `.context-hub.conf` > global `~/.config/claude/graphiti-context-hub.conf`
- MCP server configs are stored in `~/.claude.json`
- Serena and Context7 are plugins, not MCPs - install via `claude plugins install`
- Group ID can be set in config files or will use 'main' as default
