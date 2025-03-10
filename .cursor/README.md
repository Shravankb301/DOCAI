# Cursor Rules for DocAI Project

This directory contains rules for the Cursor AI assistant to help with the development of the DocAI project. These rules provide guidance and best practices for different aspects of the project.

## Available Rules

### 1. FastAPI Best Practices
- **File**: `rules/fastapi.mdc`
- **Applies to**: Backend Python files (`backend/**/*.py`)
- **Description**: Best practices for building robust, efficient, and maintainable FastAPI applications.

### 2. Next.js Best Practices
- **File**: `rules/nextjs.mdc`
- **Applies to**: Frontend Next.js files
- **Description**: Best practices for developing Next.js applications with modern UI/UX frameworks.

### 3. Orchestration Best Practices
- **File**: `rules/orchestration.mdc`
- **Applies to**: Shell scripts, Docker Compose files, and Dockerfiles (`*.sh`, `docker-compose.yml`, `*/Dockerfile`)
- **Description**: Best practices for service orchestration, shell scripting, and containerization.

### 4. Supabase Integration Best Practices
- **File**: `rules/supabase.mdc`
- **Applies to**: Supabase-related files in both backend and frontend (`backend/app/utils/supabase*.py`, `frontend/src/**/supabase*.ts`, `frontend/src/**/supabase*.js`)
- **Description**: Best practices for integrating Supabase with both backend and frontend applications.

### 5. AI Model Integration Best Practices
- **File**: `rules/ai_models.mdc`
- **Applies to**: AI model-related files in the backend (`backend/app/models/*.py`, `backend/app/utils/model*.py`)
- **Description**: Best practices for integrating and using transformer models for document analysis.

### 6. Continuous Testing Best Practices
- **File**: `rules/testing.mdc`
- **Applies to**: Test files in both backend and frontend (`backend/tests/**/*.py`, `frontend/src/**/*.test.ts`, etc.)
- **Description**: Best practices for continuous testing, test-driven development, and ensuring implementations are working correctly.

### 7. CI/CD and Automated Rebuilding Best Practices
- **File**: `rules/ci_cd.mdc`
- **Applies to**: CI/CD configuration files (`.github/workflows/*.yml`, `scripts/ci/*.sh`, etc.)
- **Description**: Best practices for continuous integration, automated testing, and rebuilding failing implementations.

## How to Use

These rules are automatically applied by the Cursor AI assistant when working with files that match the specified glob patterns. The rules provide guidance on best practices, code structure, and implementation details for different aspects of the project.

## Updating Rules

To update the rules, you can either:

1. Edit the rule files directly in the `.cursor/rules/` directory.
2. Run the `update_rules.sh` script in the project root to regenerate all rules.

## Adding New Rules

To add a new rule:

1. Create a new `.mdc` file in the `.cursor/rules/` directory.
2. Follow the format of existing rule files, including the YAML frontmatter with `description`, `globs`, and `alwaysApply` fields.
3. Add the rule content in Markdown format.

## Rule Format

Each rule file should have the following structure:

```
---
description: Brief description of the rule.
globs: ["pattern1", "pattern2"]
alwaysApply: false
---

# Rule Title

Rule content in Markdown format...
```

- `description`: A brief description of the rule.
- `globs`: An array of glob patterns that determine which files the rule applies to.
- `alwaysApply`: Whether the rule should always be applied regardless of the file being edited. 