# SECURITY.md - Security and Secret Management

## 🔐 SECURITY AND SECRET MANAGEMENT

### **Pragmatic Security Approach**

Implement security best practices without over-engineering. Focus on protecting actual sensitive data rather than theoretical threats.

### **Security Best Practices**
1. **Environment-Based Secrets**: Proper separation of dev/staging/production secrets
2. **Input Validation**: Comprehensive validation of all user inputs
3. **Authentication Security**: JWT with proper refresh token handling
4. **Rate Limiting**: Prevent abuse with intelligent rate limiting
5. **Audit Logging**: Track security events and access patterns

## Security Considerations

- JWT authentication with refresh tokens
- Input validation and sanitization
- Rate limiting on all endpoints
- Encrypted data at rest and in transit
- Regular security scanning and updates
- Docker security best practices

### **Infisical Services**
- **Web UI**: http://localhost:8080 - Infisical dashboard for secret management
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for sessions and performance
- **API**: RESTful API for programmatic access

### **Management Commands**
```bash
# Service Management
./infisical-manage.sh start      # Start all services
./infisical-manage.sh stop       # Stop all services
./infisical-manage.sh status     # Check service status
./infisical-manage.sh logs       # View logs

# Project Setup
./infisical-manage.sh setup-project  # Guide for creating PromptEvolver project
./infisical-manage.sh cli            # Install Infisical CLI

# Maintenance
./infisical-manage.sh backup     # Backup data and config
./infisical-manage.sh reset      # DANGER: Delete all data
```

### **AVSHA-Organized Secret Structure**

#### **Feature-Based Secret Organization**
Following our AVSHA framework, secrets are organized by feature:

**Authentication Feature Secrets:**
```
Environment: development
├── JWT_SECRET_KEY           # JWT token signing key
├── JWT_REFRESH_SECRET       # JWT refresh token key
├── OAUTH_CLIENT_ID          # OAuth client identifier
├── OAUTH_CLIENT_SECRET      # OAuth client secret
└── SESSION_SECRET_KEY       # Session encryption key
```

**Optimization Feature Secrets:**
```
Environment: development
├── OPENAI_API_KEY          # OpenAI API access key
├── ANTHROPIC_API_KEY       # Anthropic API access key
├── PROMPTWIZARD_CONFIG     # PromptWizard configuration
├── OLLAMA_BASE_URL         # Ollama server URL
└── AI_MODEL_CONFIG         # AI model configuration
```

**Dashboard Feature Secrets:**
```
Environment: development
├── ANALYTICS_API_KEY       # Analytics service key
├── MONITORING_TOKEN        # Monitoring service token
├── GRAFANA_API_KEY         # Grafana dashboard key
├── PROMETHEUS_CONFIG       # Prometheus configuration
└── SENTRY_DSN             # Error tracking DSN
```

### **Development Workflow**

#### **Initial Setup (One-time)**
```bash
# 1. Start Infisical
./infisical-manage.sh start

# 2. Create admin account at http://localhost:8080
# 3. Download Emergency Kit PDF (CRITICAL!)
# 4. Create "PromptEvolver" project
# 5. Create environments: development, staging, production

# 6. Install CLI
npm install -g @infisical/cli
infisical login --domain=http://localhost:8080
```

#### **Daily Development Workflow**
```bash
# 1. Ensure Infisical is running
./infisical-manage.sh status

# 2. Access secrets via CLI
infisical secrets get JWT_SECRET_KEY --env=development
infisical secrets set OPENAI_API_KEY "sk-..." --env=development

# 3. Export secrets to .env files
infisical export --env=development --format=dotenv > .env.development
infisical export --env=production --format=dotenv > .env.production

# 4. Use in FastAPI application
# Secrets automatically loaded from .env.development
```

### **Integration with Automation Pipeline**

#### **Enhanced security-specialist Sub-Agent**
The security-specialist agent now includes Infisical management:

```bash
# When /agents security-specialist is activated
/agents security-specialist

# Agent automatically:
# 1. Checks Infisical service status
# 2. Validates secret organization follows AVSHA structure
# 3. Ensures no hardcoded secrets in commits
# 4. Reviews secret access audit logs
# 5. Provides security recommendations
```

#### **Mandatory Secret Management Actions**
Before EVERY commit involving configuration or secrets:

```bash
# 1. Check Infisical services
./infisical-manage.sh status

# 2. Validate secret organization
infisical projects list

# 3. Export latest secrets
infisical export --env=development --format=dotenv > .env.development

# 4. Scan for hardcoded secrets (manual for now)
grep -r "sk-" --exclude-dir=.git --exclude="*.md" .

# 5. Update knowledge graph
python .claude/scripts/update_knowledge_graph.py
```

### **AVSHA Integration Points**

#### **Shared Components (Future PromptVault)**
Based on Infisical usage, we'll need these AVSHA components:

```
shared/
├── atoms/
│   ├── SecretInput/         # Masked input (like Infisical's secret forms)
│   ├── EnvironmentBadge/    # Environment indicator (dev/staging/prod)
│   └── SecretStrength/      # Secret validation indicator
├── molecules/
│   ├── SecretForm/          # Add/edit secret forms
│   ├── SecretList/          # List secrets with masking
│   └── EnvironmentSwitcher/ # Switch between environments
└── organisms/
    ├── SecretManager/       # Complete secret dashboard
    ├── ProjectManager/      # Manage secret projects/groups
    └── AuditViewer/         # View access logs and audit trail
```

#### **Feature Integration**
Each feature integrates with Infisical:

**FastAPI Backend Integration:**
```python
# app/shared/organisms/secret_loader.py
import os
from dotenv import load_dotenv

def load_development_secrets():
    """Load secrets from Infisical-exported .env file"""
    load_dotenv('.env.development')
    return {
        'jwt_secret': os.getenv('JWT_SECRET_KEY'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'database_url': os.getenv('DATABASE_URL')
    }

# app/features/authentication/config.py
from shared.organisms.secret_loader import load_development_secrets
secrets = load_development_secrets()
JWT_SECRET_KEY = secrets['jwt_secret']
```

### **Learning Objectives for PromptVault**

Using Infisical teaches us what PromptVault needs:

#### **Essential Features to Replicate**
1. **Web UI**: Simple, clean interface for secret management
2. **Environment Separation**: Clear dev/staging/prod organization
3. **CLI Integration**: Command-line tool for automation
4. **Export Functionality**: Generate .env files for applications
5. **Audit Logging**: Track who accessed what and when
6. **Project Organization**: Group secrets by application/feature

#### **Simplifications for PromptVault**
1. **Single User**: Remove team/organization features
2. **Local Storage**: File-based instead of database
3. **Basic Auth**: Master password instead of complex auth
4. **Minimal UI**: Focus on essential functionality
5. **Git Integration**: Built-in secret scanning and pre-commit hooks

#### **AVSHA Enhancements**
1. **Feature-Based Organization**: Automatic grouping by AVSHA features
2. **Framework Integration**: Native integration with our automation pipeline
3. **Component Generation**: Auto-generate secret management UI components
4. **Development Workflow**: Optimized for individual developer productivity

### **Security Best Practices (Current)**

#### **Infisical Security Rules**
1. **Emergency Kit**: Always download and safely store the Emergency Kit PDF
2. **Strong Master Password**: Use a unique, strong password for Infisical admin
3. **Environment Separation**: Never mix dev/staging/prod secrets
4. **Regular Backups**: Use `./infisical-manage.sh backup` weekly
5. **Access Monitoring**: Review audit logs in Infisical dashboard regularly

#### **Development Security Workflow**
```bash
# 1. Daily security check
./infisical-manage.sh status
infisical audit-logs --limit 10

# 2. Before commits
grep -r "sk-\|jwt_secret\|api_key" --exclude-dir=.git .
# Should return no results (except in .env files)

# 3. Rotate secrets monthly
infisical secrets update JWT_SECRET_KEY "$(openssl rand -base64 32)" --env=development

# 4. Backup before major changes
./infisical-manage.sh backup
```
