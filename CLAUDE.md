# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LingNexus is a multi-agent system built on the AgentScope framework with Claude Skills compatibility. It implements a progressive disclosure mechanism to efficiently manage large numbers of skills while minimizing token usage.

The system now includes a **competitive intelligence monitoring system** for pharmaceutical data collection and analysis.

## Project Structure

```
LingNexus/
├── lingnexus/                    # Core application module
│   ├── agent/                    # Agent creation and management
│   │   ├── react_agent.py        # Unified Agent creation entry point (USER INTERFACE)
│   │   └── agent_factory.py      # Agent factory (internal use only)
│   ├── cli/                      # Command-line interface
│   │   ├── __main__.py           # CLI main entry point
│   │   ├── interactive.py        # Interactive chat mode
│   │   └── monitoring.py         # Monitoring commands
│   ├── config/                   # Configuration management
│   │   ├── model_config.py       # Model configuration (Qwen, DeepSeek)
│   │   ├── api_keys.py           # API key management
│   │   └── agent_config.py       # Agent configuration
│   ├── scheduler/                # Task scheduling
│   │   └── monitoring.py         # Daily monitoring tasks
│   ├── storage/                  # Three-tier storage architecture
│   │   ├── raw.py                # Raw data storage (HTML/JSON)
│   │   ├── structured.py         # Structured database (SQLite + SQLAlchemy)
│   │   └── vector.py             # Vector database (ChromaDB, optional)
│   └── utils/                    # Utility modules
│       ├── skill_loader.py       # Skills loading and registration
│       └── code_executor.py      # Code execution environment
│
├── skills/                       # Claude Skills directory
│   ├── external/                 # External skills (Claude Skills format)
│   │   ├── docx/                 # Word document generation
│   │   ├── pdf/                 # PDF processing
│   │   ├── pptx/                # PowerPoint generation
│   │   └── [...other skills]
│   └── internal/                 # Internal skills (custom)
│       └── intelligence/        # Competitive intelligence monitoring
│           └── scripts/         # Data collection scripts
│               ├── clinical_trials_scraper.py  # ClinicalTrials.gov scraper
│               └── cde_scraper.py              # CDE website scraper
│
├── config/                       # Configuration files
│   └── projects_monitoring.yaml # Monitoring project configuration
│
├── examples/                     # Usage examples
│   ├── docx_agent_example.py
│   ├── progressive_agent_example.py
│   ├── monitoring_example.py
│   └── cde_scraper_example.py
│
├── tests/                        # Test files
│   ├── test_setup.py
│   ├── test_api_key.py
│   ├── test_model_creation.py
│   └── [...more tests]
│
├── scripts/                      # Utility scripts
│   ├── load_claude_skills.py    # Load Claude Skills
│   └── register_skills.py       # Register skills to system
│
├── docs/                         # Documentation
│   ├── architecture.md          # Architecture documentation
│   ├── monitoring_system.md     # Monitoring system guide
│   └── cli_guide.md             # CLI usage guide
│
└── data/                         # Data directory (runtime, not in git)
    ├── raw/                     # Raw data storage
    ├── intelligence.db          # SQLite database
    └── vectordb/                # ChromaDB vector database
```

## Directory Responsibilities

### Core Module (`lingnexus/`)

**`lingnexus/agent/` - Agent Management**
- `react_agent.py`: Unified entry point for agent creation (exposes `create_docx_agent()`, `create_progressive_agent()`)
- `agent_factory.py`: Internal factory implementation
- **Design Rule**: User code should only call `react_agent.py`, never `agent_factory.py` directly

**`lingnexus/cli/` - Command-Line Interface**
- `__main__.py`: CLI main entry point, routes all subcommands
- `interactive.py`: Interactive chat interface implementation
- `monitoring.py`: Monitoring commands implementation
- Usage: `python -m lingnexus.cli [command]`

**`lingnexus/config/` - Configuration**
- `model_config.py`: Creates Qwen and DeepSeek models via DashScope API
- `api_keys.py`: Manages API keys (env vars, .env file)
- `agent_config.py`: Agent configuration parameters

**`lingnexus/scheduler/` - Task Scheduling**
- `monitoring.py`: Daily monitoring task orchestrator
  - Loads project config (`projects_monitoring.yaml`)
  - Coordinates multiple data source scrapers
  - Cleans and validates data
  - Saves to three-tier storage

**`lingnexus/storage/` - Three-Tier Storage**
- `raw.py`: Raw data storage (preserves complete HTML/JSON)
- `structured.py`: Structured database (SQLAlchemy ORM + SQLite)
- `vector.py`: Vector database (ChromaDB, optional dependency)

**`lingnexus/utils/` - Utilities**
- `skill_loader.py`: Implements Claude Skills three-tier progressive disclosure
- `code_executor.py`: Safe code execution environment

### Skills Directory (`skills/`)

**`skills/external/` - External Skills**
- Follows Claude Skills official format
- Document generation, design, testing skills
- Each skill contains `SKILL.md`, `scripts/`, `references/`, `assets/`

**`skills/internal/` - Internal Skills**
- Custom-developed skills
- **intelligence/**: Competitive intelligence monitoring
  - ClinicalTrials.gov API v2 scraper
  - CDE website Playwright scraper (anti-detection enhanced)

### Configuration and Examples (`config/`, `examples/`, `tests/`)

**`config/`**
- `projects_monitoring.yaml`: Defines monitoring projects, keywords, data source priorities

**`examples/`**
- Complete examples for various use cases
- Demonstrates best practices

**`tests/`**
- Unit and integration tests
- Covers all core functionality

### Scripts and Documentation (`scripts/`, `docs/`)

**`scripts/`**
- `load_claude_skills.py`: Load external Claude Skills
- `register_skills.py`: Register skills to system
- `setup.sh/ps1`: Cross-platform setup scripts

**`docs/`**
- Detailed architecture, implementation, and usage documentation

### Data Directory (`data/`)

Auto-generated at runtime, not in version control:
- `raw/`: Raw data (organized by source and date)
- `intelligence.db`: SQLite structured database
- `vectordb/`: ChromaDB vector database

## Common Commands

### Installation and Setup
```bash
# Install dependencies
uv sync

# Install CDE scraper dependencies (if using monitoring system)
uv add playwright tabulate
uv run python -m playwright install chromium

# Install vector database (optional, for semantic search)
uv add chromadb

# Set up API key
cp .env.example .env
# Edit .env with your DASHSCOPE_API_KEY
```

**Dependencies**:
- **Required**: agentscope, sqlalchemy, requests
- **For CDE scraper**: playwright, tabulate
- **Optional**: chromadb (for semantic search)
- **Optional**: Node.js (for some skills)

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
# Interactive CLI (default - chat mode)
uv run python -m lingnexus.cli
uv run python -m lingnexus.cli chat --model qwen --mode test

# Monitoring System Commands (includes CDE scraper)
uv run python -m lingnexus.cli monitor              # Monitor all projects
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
uv run python -m lingnexus.cli status               # View monitoring status
uv run python -m lingnexus.cli db                   # View database
uv run python -m lingnexus.cli db --project "司美格鲁肽"
uv run python -m lingnexus.cli db --nct NCT06989203
uv run python -m lingnexus.cli search "关键词"

# Example scripts
uv run python examples/docx_agent_example.py
uv run python examples/progressive_agent_example.py
uv run python examples/monitoring_example.py

# CDE Scraper (direct execution for debugging)
python examples/cde_scraper_example.py
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

#### `lingnexus/cli/` - Unified CLI Entry Point
- **`__main__.py`**: Main CLI entry point with subcommand routing
  - `chat` - Interactive agent conversation (default)
  - `monitor` - Execute monitoring tasks
  - `status` - View monitoring system status
  - `db` - Query structured database
  - `search` - Semantic search in vector database
- **`interactive.py`**: Interactive chat interface
- **`monitoring.py`**: Monitoring-related commands

#### `lingnexus/scheduler/` - Monitoring System
- **`monitoring.py`**: Daily monitoring task orchestrator
  - Loads project configuration from `config/projects_monitoring.yaml`
  - Manages data source priority
  - Coordinates scrapers (ClinicalTrials.gov, CDE, Insight)
  - Cleans and validates data
  - Saves to three-tier storage

#### `lingnexus/storage/` - Three-Tier Storage Architecture
- **`raw.py`**: Raw data storage (HTML/JSON)
  - Preserves complete original data
  - Organized by project and date
  - Location: `data/raw/`
- **`structured.py`**: SQLAlchemy ORM + SQLite
  - Projects, clinical trials, applications tables
  - Location: `data/intelligence.db`
- **`vector.py`**: ChromaDB vector database (optional)
  - Semantic search capabilities
  - Location: `data/vectordb/`
  - Auto-disabled if ChromaDB not installed

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
  - `intelligence/` - Competitive intelligence monitoring
    - `scripts/clinical_trials_scraper.py` - ClinicalTrials.gov API v2 scraper
    - `scripts/cde_scraper.py` - CDE website scraper (Playwright)

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

### Monitoring System Usage
```python
# Execute monitoring
from lingnexus.scheduler.monitoring import DailyMonitoringTask

task = DailyMonitoringTask()
results = task.run(project_names=["司美格鲁肽"])

# Query database
from lingnexus.storage.structured import StructuredDB

db = StructuredDB()
trials = db.get_project_trials("司美格鲁肽", limit=20)
for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")

db.close()
```

## CLI Commands

### Unified CLI (Recommended)
The CLI has been unified with multiple subcommands:

**Monitoring Commands** (includes CDE scraper):
```bash
python -m lingnexus.cli monitor [--project NAME]     # Execute monitoring (triggers CDE scraper)
python -m lingnexus.cli status                        # View system status
python -m lingnexus.cli db [--project NAME] [--nct ID]  # Query database
python -m lingnexus.cli search QUERY [--project NAME]   # Semantic search
```

**Interactive Chat**:
```bash
python -m lingnexus.cli                      # Default: chat mode
python -m lingnexus.cli chat [OPTIONS]       # Explicit chat mode
```

**CDE Scraper**:
- **Integrated**: Use `monitor` command to trigger CDE scraper with automatic data storage
- **Standalone**: Use `python examples/cde_scraper_example.py` for direct debugging
- CDE scraper requires `headless=False` (shows browser window) to bypass anti-bot detection

### Interactive Chat Commands
When in chat mode, these commands (all start with `/`) are available:
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

### Monitoring System Development

**Adding New Data Sources**:
1. Create scraper in `skills/internal/intelligence/scripts/`
2. Add scraper method to `lingnexus/scheduler/monitoring.py`
3. Update `config/projects_monitoring.yaml` with new source

**Date Handling**:
- SQLite Date type requires Python `date` objects, not strings
- System auto-converts via `_clean_dates()` method
- Supported formats: `YYYY-MM-DD`, `YYYY-MM`, `YYYY`

**Optional Dependencies**:
- **playwright**: Required for CDE scraper (install with `uv add playwright`)
- **tabulate**: Required for database query display (install with `uv add tabulate`)
- **ChromaDB**: Vector database for semantic search (optional, install with `uv add chromadb`)
  - System gracefully degrades if not installed
  - Always check: `try: from lingnexus.storage.vector import VectorDB`
  - Warn users if optional features unavailable

**Configuration File**:
- Location: `config/projects_monitoring.yaml`
- Contains project definitions and data source priorities
- Monitored projects: 司美格鲁肽 (Semaglutide)

## CDE Scraper Usage

### Two Ways to Use CDE Scraper

**Method 1: Through CLI Monitoring System (Recommended)**

```bash
# Trigger CDE scraper through monitoring system
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# View collected data
uv run python -m lingnexus.cli db --project "司美格鲁肽"
```

**Advantages**:
- Automatically integrated into monitoring workflow
- Data automatically saved to three-tier storage architecture
- Supports multi-source coordination
- Automatic data cleaning and indexing
- Uses `headless=False` (shows browser window) to bypass anti-bot detection

**Method 2: Direct Script Execution (For Debugging)**

```bash
# Must use Python directly (not uv run)
python examples/cde_scraper_example.py
```

**Important Notes**:
- CDE scraper requires `headless=False` to bypass anti-bot detection
- Direct script execution cannot use `uv run` (causes asyncio loop conflict)
- First run automatically downloads Chromium browser (~150MB)

**Anti-Detection Features**:
- Disables automation detection flags (`--disable-blink-features=AutomationControlled`)
- Real browser fingerprints (User-Agent, viewport, timezone, geolocation)
- JavaScript injection to override `navigator.webdriver`
- Human behavior simulation (mouse movement, scrolling, random delays)
- Smart retry mechanism (max 3 attempts)
- Page content detection (identifies blocked pages)

**Extracted Fields**:
- Registration number (registration_number)
- Trial status (status)
- Drug name (company)
- Indication (indication)
- URL link

## Important Notes

### Data Storage
- **Raw data**: `data/raw/{source}/{date}/` - Original HTML/JSON (do not modify)
- **Structured DB**: `data/intelligence.db` - SQLite (queryable)
- **Vector DB**: `data/vectordb/` - ChromaDB (optional, for semantic search)
- All data directories are excluded from git via `.gitignore`

**Note**: The system gracefully degrades without ChromaDB. Core functionality (data collection, storage, querying) works perfectly without vector database. Only semantic search is unavailable.

### Testing Monitoring System
```bash
# First, install required dependencies
uv add playwright tabulate
uv run python -m playwright install chromium

# Test basic monitoring (includes CDE scraper)
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# View results
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# Check system status
uv run python -m lingnexus.cli status

# Test CDE scraper directly (for debugging)
python examples/cde_scraper_example.py
```

**Note**: CDE scraper will show browser window (`headless=False`) to bypass anti-bot detection. This is normal behavior.

### Documentation References
- **Monitoring System**: `docs/monitoring_system.md` - Complete guide
- **Implementation Summary**: `docs/FINAL_IMPLEMENTATION_SUMMARY.md`
- **Architecture**: `docs/architecture.md` - Overall system design
- **CLI Guide**: `docs/cli_guide.md` - Detailed CLI usage
