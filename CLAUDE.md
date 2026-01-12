# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LingNexus is a **Monorepo** containing two main projects:

1. **Framework** (`lingnexus-framework`): Multi-agent system with Claude Skills compatibility
2. **Platform** (`lingnexus-platform`): Low-code web platform for building AI agents (in development)

The framework implements a **progressive disclosure mechanism** to efficiently manage large numbers of skills while minimizing token usage, with a **competitive intelligence monitoring system** for pharmaceutical data collection.

## Monorepo Structure

```
LingNexus/
├── packages/
│   ├── framework/              # Framework package (v0.2.0)
│   │   ├── lingnexus/          # Core framework code
│   │   ├── skills/             # Claude Skills
│   │   ├── examples/           # Usage examples
│   │   ├── tests/              # Framework tests
│   │   └── pyproject.toml      # Package config
│   │
│   └── platform/              # Platform package (v1.0.0)
│       ├── backend/           # FastAPI backend
│       └── frontend/          # Vue 3 frontend
│
├── docs/                      # Project documentation
├── scripts/                   # Development scripts
├── config/                    # Configuration files
└── data/                      # Data directory (runtime, not in git)
```

## Framework Structure

```
packages/framework/lingnexus/
├── agent/                     # Agent creation and management
│   ├── react_agent.py         # Unified entry point (USER INTERFACE) ⭐
│   └── agent_factory.py       # Agent factory (internal use only)
├── cli/                       # Command-line interface
│   ├── __main__.py           # CLI main entry point
│   ├── interactive.py        # Interactive chat mode
│   └── monitoring.py         # Monitoring commands
├── config/                    # Configuration management
│   ├── model_config.py       # Model config (Qwen, DeepSeek)
│   ├── api_keys.py           # API key management
│   └── agent_config.py       # Agent configuration
├── scheduler/                 # Task scheduling
│   └── monitoring.py         # Daily monitoring tasks
├── storage/                   # Three-tier storage architecture
│   ├── raw.py                # Raw data storage (HTML/JSON)
│   ├── structured.py         # Structured database (SQLite + SQLAlchemy)
│   └── vector.py             # Vector database (ChromaDB, optional)
└── utils/                     # Utility modules
    ├── skill_loader.py       # Skills loading and registration
    └── code_executor.py      # Code execution environment
```

## Critical Architecture Rules

### Unified Entry Point Principle

**CRITICAL**: Always use `lingnexus/agent/react_agent.py` as the unified entry point for agent creation. Never directly call `AgentFactory` from user code.

```
User/CLI Layer
    ↓
react_agent.py (unified entry point)
    ↓
agent_factory.py (factory implementation)
    ↓
Underlying components (model_config, skill_loader)
```

### Key Files

**`packages/framework/lingnexus/agent/react_agent.py`**
- **Purpose**: User-facing API for agent creation
- **Functions**:
  - `create_docx_agent()` - Create docx agent (traditional method)
  - `create_progressive_agent()` - Create progressive disclosure agent (recommended)
- **Usage**: All agent creation should go through this file

**`packages/framework/lingnexus/agent/agent_factory.py`**
- **Purpose**: Internal factory implementation
- **Class**: `AgentFactory`
- **Usage**: Should only be called by `react_agent.py`

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
cd packages/framework
uv run pytest

# Run specific tests
uv run python tests/test_setup.py
uv run python tests/test_api_key.py
uv run python tests/test_model_creation.py
uv run python tests/test_skill_registration.py
uv run python tests/test_agent_creation.py
uv run python tests/test_cli.py
uv run python tests/test_architecture.py
uv run python tests/test_code_executor.py
```

### Running the Application

**Interactive CLI (default - chat mode)**

```bash
cd packages/framework
uv run python -m lingnexus.cli
uv run python -m lingnexus.cli chat --model qwen --mode test
```

**Monitoring System Commands** (includes CDE scraper)

```bash
uv run python -m lingnexus.cli monitor              # Monitor all projects
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
uv run python -m lingnexus.cli status               # View monitoring status
uv run python -m lingnexus.cli db                   # View database
uv run python -m lingnexus.cli db --project "司美格鲁肽"
uv run python -m lingnexus.cli db --nct NCT06989203
uv run python -m lingnexus.cli search "关键词"
```

**Example Scripts**

```bash
uv run python examples/docx_agent_example.py
uv run python examples/progressive_agent_example.py
uv run python examples/monitoring_example.py

# CDE Scraper (direct execution for debugging)
python examples/cde_scraper_example.py
```

## Progressive Disclosure System

The system implements Claude Skills' three-tier progressive disclosure mechanism:

**Phase 1 - Metadata Layer** (~100 tokens/skill)
- Initial loading includes only skill names and descriptions
- Enables efficient skill discovery across many skills

**Phase 2 - Instruction Layer** (~5k tokens)
- Dynamic loading of full SKILL.md content when needed
- Loaded via `load_skill_instructions(skill_name)` tool

**Phase 3 - Resource Layer**
- **References**: Loaded on-demand from `references/` directory
- **Assets**: Accessed via file system through `get_skill_resource_path()`
- **Scripts**: Executed through file system access

## Skill Types and Locations

```
packages/framework/skills/
├── external/           # External Skills (Claude Skills compatible format)
│   ├── docx/          # Word document generation
│   ├── pdf/           # PDF processing
│   ├── pptx/          # PowerPoint generation
│   ├── xlsx/          # Excel processing
│   └── [...more skills]
└── internal/           # Internal Skills (custom-developed)
    ├── intelligence/    # Competitive intelligence monitoring
    │   └── scripts/
    │       ├── clinical_trials_scraper.py  # ClinicalTrials.gov API v2
    │       └── cde_scraper.py              # CDE website (Playwright)
    └── js-checker/      # JavaScript syntax checker
```

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
from lingnexus.react_agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(model_type=ModelType.QWEN)
response = await agent(Msg(name="user", content="Create a Word document"))
```

### Progressive Agent (Recommended)

```python
from lingnexus.react_agent import create_progressive_agent

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
python -m lingnexus.cli monitor [--project NAME]     # Execute monitoring
python -m lingnexus.cli status                        # View system status
python -m lingnexus.cli db [--project NAME] [--nct ID]  # Query database
python -m lingnexus.cli search QUERY [--project NAME]   # Semantic search
```

**Interactive Chat**:

```bash
python -m lingnexus.cli                      # Default: chat mode
python -m lingnexus.cli chat [OPTIONS]       # Explicit chat mode
```

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
3. **Implement new agent types** by adding functions to `react_agent.py`, not directly to user code
4. **Follow the three-tier progressive disclosure pattern** for skill access
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
- ChromaDB (vector DB) is optional - system gracefully degrades
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
- **Raw data**: `packages/framework/data/raw/{source}/{date}/` - Original HTML/JSON (do not modify)
- **Structured DB**: `packages/framework/data/intelligence.db` - SQLite (queryable)
- **Vector DB**: `packages/framework/data/vectordb/` - ChromaDB (optional, for semantic search)
- All data directories are excluded from git via `.gitignore`

### Testing Monitoring System

```bash
# Test basic monitoring (includes CDE scraper)
cd packages/framework
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
- **Architecture**: `docs/development/architecture.md` - Overall system design
- **CLI Guide**: `docs/cli_guide.md` - Detailed CLI usage

## Platform Development

The Platform package provides a low-code web interface for building and managing AI agents.

### Platform Structure

```
packages/platform/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── skills.py       # Skills CRUD
│   │       ├── agents.py       # Agents CRUD & execution
│   │       ├── monitoring.py   # Monitoring data
│   │       └── marketplace.py  # Skills Marketplace ⭐
│   ├── core/
│   │   ├── security.py         # JWT + password hashing
│   │   └── deps.py            # Dependencies (auth, etc.)
│   ├── db/
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── session.py         # Database session
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/
│   │   └── agent_service.py   # Agent execution service
│   └── main.py               # FastAPI app entry point
│
└── frontend/                   # Vue 3 Frontend
    ├── src/
    │   ├── api/              # API clients
    │   │   ├── client.ts     # Axios configuration
    │   │   ├── marketplace.ts # Marketplace API ⭐
    │   │   └── ...
    │   ├── stores/           # Pinia stores
    │   │   ├── marketplace.ts # Marketplace store ⭐
    │   │   └── ...
    │   ├── views/            # Page components
    │   │   ├── MarketplaceView.vue ⭐
    │   │   ├── MarketplaceSkillDetailView.vue ⭐
    │   │   └── ...
    │   ├── router/           # Vue Router config
    │   └── layouts/          # Layout components
    └── package.json
```

### Skills Marketplace Features

**Backend API Endpoints** (`/api/v1/marketplace/`):

```python
# GET /marketplace/skills - List marketplace skills
# Query params: category, sharing_scope, search, sort_by, department, is_official
# Returns: List[MarketplaceSkill]

# GET /marketplace/skills/{id} - Get skill details
# Returns: MarketplaceSkill

# POST /marketplace/skills/{id}/try - Try skill without login
# Body: { message: str }
# Returns: TrySkillResponse

# POST /marketplace/skills/{id}/create-agent - Create agent from skill
# Body: CreateAgentFromSkillRequest
# Returns: Agent

# POST /marketplace/skills/{id}/save - Save skill to favorites
# Returns: { message: str }

# DELETE /marketplace/skills/{id}/save - Unsave skill
# Returns: 204 No Content

# POST /marketplace/skills/{id}/rate - Rate skill
# Body: { rating: int (1-5), comment?: str }
# Returns: SkillRating

# GET /marketplace/my/saved - Get user's saved skills
# Returns: List[MarketplaceSkill]
```

**Database Models**:

```python
class User(Base):
    # Basic: id, username, email, hashed_password, full_name
    # Status: is_active, is_superuser
    # Marketplace: department, role (user/admin/super_admin), xp, level
    # Timestamps: created_at, updated_at

class Skill(Base):
    # Basic: id, name, category (external/internal), content, meta
    # Status: is_active, version
    # Marketplace: sharing_scope (private/team/public), department, is_official
    # Statistics: usage_count, rating, rating_count
    # Documentation: documentation
    # Timestamps: created_at, updated_at
    # Relations: creator, agent_skills, saved_by, ratings

class SavedSkill(Base):
    # User's saved skills
    user_id: int
    skill_id: int
    # Unique constraint on (user_id, skill_id)

class SkillRating(Base):
    # User ratings for skills
    user_id: int
    skill_id: int
    rating: int  # 1-5
    comment: Optional[str]
    # Unique constraint on (user_id, skill_id)
```

**Permission System**:

Access control based on `sharing_scope`:

- **`public`**: Anyone can access (no login required)
- **`team`**: Only same department users or creator
- **`private`**: Only creator

### Platform Development Commands

**Backend Development**:

```bash
cd packages/platform/backend

# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --port 8000

# Run with auto-reload and specific host
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# View API docs
# Open http://localhost:8000/docs in browser
```

**Frontend Development**:

```bash
cd packages/platform/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Key Development Guidelines

**Authentication**:

- JWT-based authentication with access tokens
- Optional authentication for public endpoints
- Use `get_current_user` for required auth
- Use `get_current_user_optional` for optional auth

**Permission Checks**:

```python
def _can_access_skill(skill: Skill, user: Optional[User]) -> bool:
    # Public skills: everyone
    if skill.sharing_scope == "public":
        return True

    # No user: only public
    if user is None:
        return False

    # Superuser: everything
    if user.is_superuser:
        return True

    # Private: only creator
    if skill.sharing_scope == "private":
        return skill.created_by == user.id

    # Team: creator or same department
    if skill.sharing_scope == "team":
        return skill.created_by == user.id or skill.department == user.department

    return False
```

**Agent Execution**:

- Platform connects to Framework's `create_progressive_agent()`
- Execution service in `services/agent_service.py`
- Tracks execution history in `AgentExecution` table
- Returns: status, output_message, error_message, tokens_used, execution_time

### Frontend Architecture

**Vue 3 Composition API**:

```typescript
// Marketplace Store
import { useMarketplaceStore } from '@/stores'

const marketplaceStore = useMarketplaceStore()

// Fetch marketplace skills
await marketplaceStore.fetchMarketplaceSkills({
  search: 'docx',
  category: 'external',
  sort_by: 'rating'
})

// Try a skill
await marketplaceStore.tryMarketplaceSkill(skillId, {
  message: 'Create a Word document'
})

// Create agent from skill
await marketplaceStore.createAgentFromSkill(skillId, {
  agent_name: 'My Docx Agent',
  model_name: 'qwen-max',
  temperature: 0.7
})
```

**Router Configuration**:

- `/marketplace` - Public access, no login required
- `/` - Requires authentication
- Route guards in `router/index.ts`

### Testing Marketplace Features

**Setup Test Data**:

1. Register a user: `POST /api/v1/auth/register`
2. Login: `POST /api/v1/auth/login`
3. Create skills with different `sharing_scope`
4. Test permission-based access

**Test Workflow**:

```bash
# 1. Start backend
cd packages/platform/backend
uv run uvicorn main:app --reload

# 2. Start frontend (new terminal)
cd packages/platform/frontend
npm run dev

# 3. Access application
# Open http://localhost:5173
# Register/Login → Browse Marketplace → Try Skills → Create Agents
```

### Platform Framework Integration

**⚠️ Current Architecture (Temporary Solution)**:

The Platform currently uses a **temporary direct-import approach** where the Backend directly imports Framework code:

```python
# Backend: services/agent_service.py
from lingnexus import create_progressive_agent
from lingnexus.config import init_agentscope

# Initialize AgentScope
init_agentscope()

# Create agent
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.7,
)
```

**Advantages**:
- ✅ Fast development and easy debugging
- ✅ No network latency
- ✅ Suitable for single-machine deployment

**Limitations**:
- ❌ Backend cannot be deployed independently
- ❌ Tight coupling violates microservice principles
- ❌ Cannot scale independently
- ❌ Resource sharing without isolation

**⚠️ Important**: This is a **temporary solution** for development/testing only.

**Future Architecture (Planned)**:

Production environment should use:
- **Microservices Architecture**: Framework as standalone HTTP service
- Platform Backend calls Framework via REST API
- Independent deployment and scaling
- See: `docs/architecture.md#platform-与-framework-架构` for full migration plan

**Workspace Dependencies**:

Platform automatically imports Framework through uv workspace:
- Changes to Framework are immediately available
- No need to reinstall packages
- Shared dependencies managed at root level

**For detailed architecture documentation**, see:
- `docs/architecture.md` - Complete Platform/Framework architecture analysis
- Migration plan with Phase 1-5 implementation steps

### Known Issues and Solutions

**Issue**: bcrypt version incompatibility
**Solution**: Using SHA256 hashing instead (`core/security.py`)

**Issue**: SQLAlchemy reserved keyword `metadata`
**Solution**: Renamed to `meta` in Skill model

**Issue**: websockets 15.0 incompatibility
**Solution**: Downgraded to websockets 12.0

### Future Platform Features

**Planned** (from design document):
- Workflow Studio (visual orchestration)
- Team collaboration features
- Gamification (XP, levels, badges, leaderboards)
- Intelligent recommendations
- One-click deployment
- Audit logs (FDA 21 CFR Part 11 compliant)

See `docs/platform/PLATFORM_FRONTEND_DESIGN.md` for complete design specification.

## Monorepo Workspace

This project uses **uv workspace** feature for local package dependencies:
- Framework can be developed independently
- Platform depends on Framework through workspace
- Changes to Framework are immediately available to Platform
- No need to reinstall packages when developing

For more information, see:
- `MIGRATION_GUIDE.md` - v0.2.0 migration guide
- `REFACTOR_GUIDE.md` - Detailed refactoring process
- `docs/development/architecture.md` - System architecture

## Version History

### v1.0.1 (2025-01-12)

**Platform Features**:
- ✨ Agent Creation
  - Skill multi-selection (searchable, filterable)
  - Complete configuration options (model, temperature, tokens, system prompt)
  - Display associated skills in agent list
- ✨ Agent Execution
  - Real-time execution dialog
  - Execution result display (output, error, tokens, time)
  - Complete execution history tracking
  - View execution details
- ✨ Skills Synchronization
  - Auto-import from Framework
  - Sync statistics (created, updated, skipped)
  - Force update option
- ✨ Marketplace Quick Create
  - One-click agent creation from skills
  - Pre-filled configuration
  - Navigate to agent list after creation
- ⚠️ Architecture documentation updated
  - Explains current temporary solution pros/cons
  - Future microservices migration plan

**Bug Fixes**:
- 🐛 Fixed JWT Token authentication (sub field type)
- 🐛 Fixed skill data type on agent creation
- 🐛 Fixed Pydantic validation error on agent list
- 🐛 Fixed database field issue on agent execution
- 🐛 Fixed Framework import path (lingnexus.agent → lingnexus)

### v1.0.0 (2025-01-11)

**Platform Initial Release**:
- ✨ Skills Marketplace 2.0
- ✨ Permission management (private/team/public)
- ✨ Agent execution functionality
- ✨ Complete Vue 3 frontend

### v0.2.0 (2025-01-10)

**Framework Monorepo Refactoring**:
- ✨ Restructured to Monorepo architecture
- ✨ Separated Framework and Platform packages
- ✨ Complete documentation system
- ✨ CDE scraper (anti-detection enhanced)
- ✨ Human behavior simulation
- ✨ Smart retry mechanism

### v0.1.9 (2025-01-XX)

**Framework Initial Release**:
- ✨ AgentScope multi-agent system
- ✨ Claude Skills compatibility
- ✨ Progressive disclosure mechanism
- ✨ ClinicalTrials.gov data collection
- ✨ Three-tier storage architecture
