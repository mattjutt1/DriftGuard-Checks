# 📁 Project Structure Overview

## 🏗️ Clean & Organized Directory Layout

```
prompt-wizard/
│
├── 🔒 .private/                    # PROPRIETARY DATA (Git-ignored)
│   ├── business-research/          # Business analysis & validation
│   ├── market-analysis/            # Market research & sizing
│   ├── competitive-analysis/       # Competitive intelligence
│   ├── technical-research/         # PromptWizard research docs
│   └── screenshots/                # Private screenshots
│
├── 📱 apps/                        # Applications
│   └── driftguard-checks-app/      # GitHub App implementation
│
├── 🌐 nextjs-app/                  # Next.js frontend application
│
├── 📚 docs/                        # Public documentation
│   ├── security/                   # Security reports & audits
│   ├── driftguard/                 # DriftGuard documentation
│   └── development/                # Development guides
│
├── 🛠️ scripts/                     # Automation scripts
│   ├── setup/                      # Installation & setup
│   ├── security/                   # Security scanning
│   └── deployment/                 # Deployment automation
│
├── 🚀 deployment/                  # Deployment configurations
│   ├── huggingface/                # HF Space deployments
│   ├── infisical/                  # Secret management
│   └── docker/                     # Docker configurations
│
├── 💼 workspace/                   # Operational data
│   ├── data/                       # Working data
│   ├── logs/                       # Application logs
│   ├── results/                    # Processing results
│   └── prompts/                    # Prompt templates
│
├── 🧪 tests/                       # Test suites
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
│
├── 📦 library/                     # Shared libraries
├── 🎯 platform/                    # Platform components
├── ⚙️ configs/                     # Configuration files
├── 📋 schemas/                     # Data schemas
├── 🗂️ examples/                    # Example implementations
├── 🗄️ attic/                       # Archived/old code
├── 🐍 venv/                        # Python virtual environment
│
└── 📄 Root Files
    ├── README.md                   # Project documentation
    ├── LICENSE                     # MIT License
    ├── CLAUDE.md                   # Claude Code instructions
    ├── Makefile                    # Build automation
    ├── Dockerfile                  # Container definition
    └── .gitignore                  # Git exclusions
```

## 🔐 Security & Privacy

### Protected Directories (Git-ignored)
- `.private/` - All proprietary research and business data
- `.env` files - Environment variables and secrets
- `venv/` - Virtual environment
- `node_modules/` - Dependencies

### Public Directories
- `docs/` - Only technical documentation (no business data)
- `apps/` - Application source code
- `scripts/` - Automation tools
- `tests/` - Test suites

## 📊 Organization Benefits

✅ **Clean Root Directory** - Only essential files remain in root
✅ **Logical Grouping** - Related files grouped by purpose
✅ **Security First** - Proprietary data in .private (Git-ignored)
✅ **Easy Navigation** - Clear directory names with icons
✅ **Scalable Structure** - Ready for growth and new features

## 🚀 Quick Access Paths

```bash
# Your proprietary research (private)
cd .private/business-research/

# DriftGuard application
cd apps/driftguard-checks-app/

# Security tools
cd scripts/security/

# Deployment configs
cd deployment/

# Working data
cd workspace/
```

---
*Last Updated: August 10, 2025*
*Organization: Systematic cleanup preserving application integrity*
