# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LingNexus is a multi-agent system built on the AgentScope framework with Claude Skills compatibility. It implements a progressive disclosure mechanism to efficiently manage large numbers of skills while minimizing token usage.

## Common Commands

### Installation and Setup
```bash
# Install dependencies
uv sync

# Set up API key
cp .env.example .env
# Edit .env with your DASHSCOPE_API_KEY
```

### Development
```bash
# Format code
uv run ruff format .

# Check code quality
uv run ruff check .
```

### Testing
```bash
# Run all tests
uv run python tests/test_setup.py

# Run specific tests
uv run python tests/test_api_key.py
uv run python tests/test_model_creation.py
uv run python tests/test_skill_registration.py
uv run python tests/test_agent_creation.py
uv run python tests/test_cli.py
uv run python tests/test_architecture.py
uv run python tests/test_code_executor.py
```

### Running the Application
```bash
# Interactive CLI (recommended)
uv run python -m lingnexus.cli

# With specific options
uv run python -m lingnexus.cli --model deepseek --mode chat --studio

# Example scripts
uv run python examples/docx_agent_example.py
uv run python examples/progressive_agent_example.py
```

## Architecture

### Unified Entry Point Principle

**Critical**: Always use `lingnexus/agent/react_agent.py` as the unified entry point for agent creation. Never directly call `AgentFactory` from user code.

```
User/CLI Layer
    ↓
react_agent.py (unified entry point)
    ↓
agent_factory.py (factory implementation)
    ↓
Underlying components (model_config, skill_loader)
```

### Key Components

#### `lingnexus/agent/react_agent.py`
- **Purpose**: User-facing API for agent creation
- **Functions**:
  - `create_docx_agent()` - Create docx agent (traditional method)
  - `create_progressive_agent()` - Create progressive disclosure agent (recommended)
- **Usage**: All agent creation should go through this file

#### `lingnexus/agent/agent_factory.py`
- **Purpose**: Internal factory implementation
- **Class**: `AgentFactory`
- **Usage**: Should only be called by `react_agent.py`

#### `lingnexus/config/model_config.py`
- Creates Qwen (通义千问) and DeepSeek models via DashScope API
- Provides unified `create_model()` interface
- Supports both model types through single API key (`DASHSCOPE_API_KEY`)

#### `lingnexus/utils/skill_loader.py`
- Loads and registers Claude Skills
- Implements progressive disclosure mechanism
- Caches metadata and instructions for performance

### Progressive Disclosure System

The system implements Claude Skills' three-tier progressive disclosure mechanism:

**Phase 1 - Metadata Layer** (~100 tokens/skill):
- Initial loading includes only skill names and descriptions
- Enables efficient skill discovery across many skills

**Phase 2 - Instruction Layer** (~5k tokens):
- Dynamic loading of full SKILL.md content when needed
- Loaded via `load_skill_instructions(skill_name)` tool

**Phase 3 - Resource Layer**:
- **References**: Loaded on-demand from `references/` directory
- **Assets**: Accessed via file system through `get_skill_resource_path()`
- **Scripts**: Executed through file system access

### Skill Types and Locations

- **External Skills**: `skills/external/` - Claude Skills compatible format
- **Internal Skills**: `skills/internal/` - Custom-developed skills

Each skill follows this structure:
```
skill-name/
├── SKILL.md              # Main skill file with YAML front matter
├── scripts/             # Executable scripts
├── references/          # Reference documents
└── assets/              # Static assets
```

## Model Configuration

Both Qwen and DeepSeek models use the DashScope API with a single `DASHSCOPE_API_KEY`:

**Qwen Models**: `qwen-max`, `qwen-plus`, `qwen-turbo`
**DeepSeek Models**: `deepseek-chat`, `deepseek-coder`

API key priority (highest to lowest):
1. Function parameter
2. Environment variable `DASHSCOPE_API_KEY`
3. `.env` file `DASHSCOPE_API_KEY`

## Agent Usage Patterns

### Traditional Agent (All Skills Loaded)
```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(model_type=ModelType.QWEN)
response = await agent(Msg(name="user", content="Create a Word document"))
```

### Progressive Agent (Recommended)
```python
from lingnexus.agent import create_progressive_agent

agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)
# Agent automatically loads skill instructions on demand
```

## CLI Commands

Interactive commands (all start with `/`):
- `/help` - Show help
- `/status` - Display current status
- `/mode <chat|test>` - Switch between chat and test modes
- `/model <qwen|deepseek>` - Switch model type
- `/execute <on|off>` - Toggle code execution
- `/studio <on|off>` - Toggle Studio integration
- `/history` - Show conversation history
- `/clear` - Clear conversation history
- `/files` - List generated files
- `/view <filename>` - View file content
- `/exit` - Exit program

## Code Quality Standards

- Line length: 100 characters (enforced by Black)
- Use Ruff for linting
- Follow async/await patterns for agent calls
- Use `Msg` objects from `agentscope.message` for agent communication

## Windows Encoding Issues

When working with subprocess or code execution, be aware of Windows encoding issues. The codebase handles this by:
- Setting `PYTHONIOENCODING=utf-8` environment variable
- Using `encoding='utf-8'` and `errors='replace'` in subprocess calls

See `docs/encoding_fix.md` for details.

## Architecture Rules

1. **Always use `react_agent.py` as the unified entry point** for agent creation
2. **Never directly call `AgentFactory`** from user code
3. **Implement new agent types** by adding functions to `react_agent.py`
4. **Follow the three-tier progressive disclosure pattern** for skill loading
5. **Use `Msg` objects** for agent communication, not plain strings

## Development Guidelines

When adding new functionality:
1. Add new agent types to `react_agent.py`, not directly to user code
2. Follow the progressive disclosure pattern for skill access
3. Use the model config module, don't instantiate models directly
4. Register skills through SkillLoader, not manually
5. Test with both Qwen and DeepSeek models
