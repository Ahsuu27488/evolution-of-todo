---
name: "sqlmodel-guide"
description: "Fetch SQLModel documentation and apply database best practices. Use when creating models, queries, or database operations (Phase II+)."
version: "1.0.0"
---

# SQLModel Database Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions SQLModel, database models, or ORM operations
- Implementation requires database tables, relationships, or queries
- User asks about SQLAlchemy, sessions, or migrations
- Phase II database development begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect SQLModel/database-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/websites/sqlmodel_tiangolo` and relevant topic
3. **Apply Patterns**: Use official SQLModel patterns for the specific feature
4. **Validate**: Ensure code follows SQLModel best practices (type hints, relationships)

## Output Format

Provide structured output:
- **Context7 Source**: `/websites/sqlmodel_tiangolo`
- **Pattern Applied**: SQLModel pattern used (model, relationship, etc.)
- **Model Structure**: Fields and types defined
- **Best Practices**: Applied optimizations

## Constraints and Rules

- ALWAYS use SQLModel for FastAPI integration (combines Pydantic + SQLAlchemy)
- ALWAYS define proper field constraints (nullable, default, index)
- Use separate models for Create/Read/Update operations
- Implement proper session management (context manager)
- Add indexes for frequently queried fields
- This skill applies to Phase II and later only

## Example

**Input**: "Create a Todo model with SQLModel"

**Output**:
```
Context7 Source: /websites/sqlmodel_tiangolo (topic: models)
Pattern Applied: SQLModel with separate schemas
Model Structure:
  class TodoBase(SQLModel):
      title: str = Field(max_length=200)
      description: str | None = None
      completed: bool = False

  class Todo(TodoBase, table=True):
      id: int | None = Field(default=None, primary_key=True)
      user_id: int = Field(foreign_key="user.id", index=True)
      created_at: datetime = Field(default_factory=datetime.utcnow)
Best Practices:
- Base model for shared fields
- Table model with primary key
- Index on foreign key
- Created timestamp with default
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `models` | Defining database tables |
| `relationships` | Foreign keys and joins |
| `session` | Database connection management |
| `create read update delete` | CRUD operations |
| `select` | Query building |
| `fastapi integration` | Using with FastAPI |
