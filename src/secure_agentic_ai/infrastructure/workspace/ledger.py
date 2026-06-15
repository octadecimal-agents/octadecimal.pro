import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  team TEXT NOT NULL,
  status TEXT NOT NULL,
  title TEXT NOT NULL,
  intent TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plan_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plan_date TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  title TEXT NOT NULL,
  source TEXT NOT NULL
);
"""

TEAMS = frozenset({"platform", "knowledge", "ops", "product"})
LEGACY_TEAM_MAP = {
    "automation": "platform",
    "security": "ops",
    "frontend": "product",
    "ux": "knowledge",
}
STATUSES = frozenset({"todo", "doing", "blocked", "done"})


@dataclass(frozen=True)
class Task:
    id: str
    team: str
    status: str
    title: str
    intent: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PlanItem:
    id: int
    plan_date: str
    sort_order: int
    title: str
    source: str


class WorkspaceLedger:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
        self._migrate_legacy_teams()

    def _migrate_legacy_teams(self) -> None:
        with self._connect() as conn:
            for old, new in LEGACY_TEAM_MAP.items():
                conn.execute("UPDATE tasks SET team = ? WHERE team = ?", (new, old))

    def list_tasks(self, team: str | None = None, status: str | None = None) -> list[Task]:
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[str] = []
        if team:
            query += " AND team = ?"
            params.append(team)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_task(row) for row in rows]

    def create_task(self, team: str, title: str, intent: str | None = None, status: str = "todo") -> Task:
        if team not in TEAMS:
            msg = f"Invalid team: {team}"
            raise ValueError(msg)
        if status not in STATUSES:
            msg = f"Invalid status: {status}"
            raise ValueError(msg)
        now = datetime.now(UTC).isoformat()
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, team, status, title, intent, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, team, status, title, intent, now, now),
            )
        return Task(task_id, team, status, title, intent, now, now)

    def update_task_status(self, task_id: str, status: str) -> Task | None:
        if status not in STATUSES:
            msg = f"Invalid status: {status}"
            raise ValueError(msg)
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (status, now, task_id))
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None

    def list_plan_items(self, plan_date: str) -> list[PlanItem]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM plan_items
                WHERE plan_date = ?
                ORDER BY sort_order ASC, id ASC
                """,
                (plan_date,),
            ).fetchall()
        return [self._row_to_plan(row) for row in rows]

    def replace_plan_items(self, plan_date: str, items: list[tuple[str, str]]) -> list[PlanItem]:
        with self._connect() as conn:
            conn.execute("DELETE FROM plan_items WHERE plan_date = ?", (plan_date,))
            for order, (title, source) in enumerate(items):
                conn.execute(
                    """
                    INSERT INTO plan_items (plan_date, sort_order, title, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    (plan_date, order, title, source),
                )
            rows = conn.execute(
                "SELECT * FROM plan_items WHERE plan_date = ? ORDER BY sort_order ASC",
                (plan_date,),
            ).fetchall()
        return [self._row_to_plan(row) for row in rows]

    def seed_demo_tasks(self) -> None:
        if self.list_tasks():
            return
        demos = [
            ("platform", "Workspace M5 dev loop", "Runbook, launchd, Octa-native board teams"),
            ("knowledge", "embed-knowledge.py T1 sync", "Ingest Knowledge paths into local RAG"),
            ("ops", "Review MCP TCC matrix", "macOS Full Disk Access recommendations"),
            ("product", "Align public demo with Workspace", "Marketing page consistency"),
        ]
        for team, title, intent in demos:
            self.create_task(team=team, title=title, intent=intent)

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            team=row["team"],
            status=row["status"],
            title=row["title"],
            intent=row["intent"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_plan(row: sqlite3.Row) -> PlanItem:
        return PlanItem(
            id=row["id"],
            plan_date=row["plan_date"],
            sort_order=row["sort_order"],
            title=row["title"],
            source=row["source"],
        )
