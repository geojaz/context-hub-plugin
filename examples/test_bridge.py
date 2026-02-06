#!/usr/bin/env python3
"""Test the bridge module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from bridge import (
    memory_query,
    memory_save,
    memory_list_recent,
    memory_get_config,
    memory_list_operations
)


def main():
    print("=== Testing Memory Bridge ===\n")

    # Test config
    print("1. Configuration:")
    config = memory_get_config()
    print(f"   Backend: {config['backend']}")
    print(f"   Group ID: {config['group_id']}\n")

    # Test operations list
    print("2. Available operations:")
    ops = memory_list_operations()
    for op in ops[:3]:
        print(f"   - {op['name']}: {op['description']}\n")

    # Test query (stub for now)
    print("3. Query test:")
    results = memory_query("test", limit=5)
    print(f"   Found {len(results)} results\n")

    # Test save (stub for now)
    print("4. Save test:")
    memory_id = memory_save("Test content", title="Test")
    print(f"   Saved with ID: {memory_id}\n")

    print("Bridge functions working!")


if __name__ == "__main__":
    main()
