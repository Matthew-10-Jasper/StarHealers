# STARHEALERS MODULE 4 — DATABASE MIGRATION GUIDE
**Database Version Management with Alembic & SQLite Batch Migrations**

---

## 1. Overview & Architecture

Module 4 utilizes **Alembic** alongside **SQLAlchemy 2.x** and **SQLite** to provide deterministic, versioned, and auditable schema migrations. 

Due to SQLite's native limitations regarding table alterations (such as adding constrained columns or dropping columns), Module 4's Alembic configuration explicitly enables `render_as_batch=True`. This ensures table alterations recreate the table cleanly within a transaction without risking data corruption or locking the local database.

---

## 2. Migration Revisions History

| Revision ID | Description | Operations | Status |
| :--- | :--- | :--- | :--- |
| **`001_baseline`** | Initial Phase 1 Schema | Creation of `mission_state`, `environmental_observations`, `mission_deviations`, `state_transitions`, `audit_log`, `queued_reports` | **Applied (Verified)** |
| **`002_units_idempotency`** | Phase 2 Scientific Units & Idempotency | Adds `canonical_value` (Float), `canonical_unit` (String), and `idempotency_key` (Indexed String) to `environmental_observations` | **Applied (Head)** |

---

## 3. Operational Commands

### Check Current Migration Version
```bash
cd backend
python -m alembic current
```

### Upgrade to Latest Revision
```bash
cd backend
python -m alembic upgrade head
```

### Downgrade (Rollback) One Revision
```bash
cd backend
python -m alembic downgrade -1
```

### Generate a New Auto-Migration
```bash
cd backend
python -m alembic revision --autogenerate -m "describe_changes"
```

---

## 4. SQLite Data Safety Guidelines
1. **Always archive database snapshot before upgrading:**
   - Pre-upgrade backup: `starhealers_m4_phase1_backup.db`
2. **Transactional Integrity:**
   - SQLite foreign key constraints are enforced on all connections via `PRAGMA foreign_keys=ON`.
3. **Offline Re-playability:**
   - Migrations can be generated as raw SQL for air-gapped environments using `python -m alembic upgrade head --sql`.
