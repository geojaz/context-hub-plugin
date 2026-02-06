"""Configuration management with hierarchical discovery."""
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass
class MemoryConfig:
    """Memory backend configuration."""
    backend: str = "graphiti"
    group_id: str = "auto"
    graphiti: Dict[str, str] = field(default_factory=lambda: {
        "endpoint": "http://localhost:8000/mcp"
    })
    forgetful: Dict[str, str] = field(default_factory=dict)


@dataclass
class Config:
    """Root configuration."""
    memory: MemoryConfig = field(default_factory=MemoryConfig)


def find_project_root() -> Optional[Path]:
    """Find project root by looking for markers."""
    cwd = Path.cwd()

    # Walk up directory tree
    for parent in [cwd] + list(cwd.parents):
        # Check for project markers
        markers = ['.git', 'pyproject.toml', 'package.json', 'pom.xml']
        if any((parent / marker).exists() for marker in markers):
            return parent

    return None


def find_config_file() -> Optional[Path]:
    """
    Find config file using hierarchical search.

    Search order:
    1. Current directory: ./.context-hub.yaml
    2. Project root: <root>/.context-hub.yaml
    3. User home: ~/.context-hub.yaml
    4. None (use defaults)
    """
    # 1. Current directory
    cwd_config = Path.cwd() / '.context-hub.yaml'
    if cwd_config.exists():
        return cwd_config

    # 2. Project root
    project_root = find_project_root()
    if project_root:
        root_config = project_root / '.context-hub.yaml'
        if root_config.exists():
            return root_config

    # 3. User home
    home_config = Path.home() / '.context-hub.yaml'
    if home_config.exists():
        return home_config

    # 4. No config found
    return None


def load_config() -> Config:
    """Load configuration from file or use defaults."""
    config_file = find_config_file()

    if not config_file:
        # Use defaults
        return Config()

    with open(config_file, 'r') as f:
        data = yaml.safe_load(f) or {}

    # Parse memory config
    memory_data = data.get('memory', {})
    memory_config = MemoryConfig(
        backend=memory_data.get('backend', 'graphiti'),
        group_id=memory_data.get('group_id', 'auto'),
        graphiti=memory_data.get('graphiti', {'endpoint': 'http://localhost:8000/mcp'}),
        forgetful=memory_data.get('forgetful', {})
    )

    return Config(memory=memory_config)


def get_git_repo_name() -> Optional[str]:
    """Extract repository name from git remote or directory."""
    try:
        # Try git remote
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse repo name from URL
        # Examples:
        #   git@github.com:user/repo.git -> repo
        #   https://github.com/user/repo.git -> repo
        url = result.stdout.strip()
        if url:
            # Extract last part before .git
            parts = url.rstrip('/').replace('.git', '').split('/')
            if parts:
                return parts[-1]

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git command failed, try .git directory name
        project_root = find_project_root()
        if project_root and (project_root / '.git').exists():
            return project_root.name

    return None


def detect_group_id(config: Config) -> str:
    """
    Detect group_id using strategy from config.

    Detection order:
    1. Explicit config value (if not "auto")
    2. Git repository name
    3. Current directory name (fallback)
    """
    # 1. Explicit override
    if config.memory.group_id != "auto":
        return config.memory.group_id

    # 2. Git repository name
    git_name = get_git_repo_name()
    if git_name:
        return git_name

    # 3. Directory fallback
    return Path.cwd().name
