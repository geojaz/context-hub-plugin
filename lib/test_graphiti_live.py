#!/usr/bin/env python3
"""
Test GraphitiBackend with live MCP server.

NOTE: This test will fail when run directly with python because MCP tools
(mcp__graphiti__*) are only available in Claude Code's execution context.
This file is kept for documentation and manual testing via Claude Code.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.backends.graphiti import GraphitiBackend
from lib.config import Config, MemoryConfig


def main():
    print("=== Testing Graphiti Backend (Live) ===\n")

    # Create backend
    config = Config(memory=MemoryConfig(backend="graphiti"))
    backend = GraphitiBackend()
    group_id = "agent-context"  # As specified in user notes

    print(f"Testing with group_id: {group_id}\n")

    # Test save
    print("1. Saving test memory...")
    try:
        memory_id = backend.save(
            "Test memory for Graphiti integration",
            group_id,
            title="Integration Test"
        )
        print(f"   ✅ Saved with ID: {memory_id}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test query
    print("2. Querying memories...")
    try:
        memories = backend.query("test", group_id, 5)
        print(f"   ✅ Found {len(memories)} memories\n")
        for m in memories[:2]:
            print(f"   - {m.content[:60]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test list recent
    print("3. Listing recent memories...")
    try:
        recent = backend.list_recent(group_id, 5)
        print(f"   ✅ Found {len(recent)} recent memories\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("Live test complete!")


if __name__ == "__main__":
    main()
