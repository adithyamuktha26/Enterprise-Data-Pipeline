# Architecture Documentation

## Data Flow Diagram
┌─────────────────┐
│   data/raw/     │
│  employees.csv  │
│  sales_q2.xlsx  │
└────────┬────────┘
│
▼
┌─────────────────┐     ┌─────────────────┐
│   src/ingest.py │────▶│  Pandas DataFrame │
│  read_csv_file()│     │  (in-memory table) │
└─────────────────┘     └────────┬────────┘
│
▼
┌─────────────────┐
│ src/validate.py │
│ EmployeeRecord  │
│  (Pydantic)     │
│                 │
│ Rules:          │
│ • Valid email   │
│ • Known dept    │
│ • Salary > 0    │
│ • Name not blank│
└────────┬────────┘
│
┌────────────┴────────────┐
▼                         ▼
┌─────────────┐           ┌─────────────┐
│   VALID     │           │   INVALID   │
│  Records    │           │   Records   │
│ (10 rows)   │           │  (0 rows)   │
└──────┬──────┘           └──────┬──────┘
│                         │
▼                         ▼
┌─────────────┐           ┌─────────────┐
│src/database.py│         │  Logged to  │
│  add_employees_│         │   console   │
│    batch()    │         │  with error │
└──────┬──────┘           │   details   │
│                  └─────────────┘
▼
┌─────────────┐
│  data/        │
│ enterprise.db │
│   (SQLite)    │
└──────┬──────┘
│
▼
┌─────────────┐
│  src/notifier.py │
│  get_department_ │
│    stats()       │
└──────┬──────┘
│
┌────────┴────────┐
▼                 ▼
┌─────────────┐   ┌─────────────┐
│   Console   │   │   Email     │
│   Output    │   │  (HTML)     │
└─────────────┘   └─────────────┘


## Key Design Decisions

### 1. SQLite for Simplicity
- No server setup required
- Single file (`enterprise.db`) easy to inspect with DB Browser
- Can migrate to PostgreSQL later by changing one connection string

### 2. Pydantic for Validation
- Type-safe validation at runtime
- Self-documenting models with `Field()` descriptions
- Automatic error messages for failed validation

### 3. Duplicate Handling
- Real-world data has duplicates
- Checking `email` uniqueness before insert prevents crashes
- Logs skipped records for audit trails

### 4. Modular Architecture
- Each module has one responsibility (SRP)
- Easy to test in isolation
- Can swap components (e.g., replace SQLite with PostgreSQL)

## Error Handling Strategy

| Error Type | Handling |
|-----------|----------|
| File not found | `FileNotFoundError` with clear message |
| Empty file | `ValueError` with explanation |
| Invalid email | Pydantic rejects row, continues processing others |
| Duplicate email | Skips row, logs warning, continues |
| Database connection | Rollback transaction, log error |
| Scheduler crash | Catches exception, logs failure, retries next cycle |