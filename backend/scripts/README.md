# Backend Scripts

Utility scripts for development and testing.

## Database (`scripts/db/`)

| Script | Purpose |
|--------|---------|
| `test_connection.py` | Test Neon PostgreSQL connection |
| `reset.py` | Reset database (deletes all data) |

## Usage

```bash
# Test database connection
python scripts/db/test_connection.py

# Reset database (WARNING: deletes all data)
python scripts/db/reset.py
```
