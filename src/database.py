"""Simple SQLite database helpers for the StampCollect app.

Provides initialization, schema creation, and basic CRUD helpers.
Designed for a single-user local app (easy to migrate to PostgreSQL later).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DB = Path.cwd() / "stamps.db"


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
	path = db_path or str(DEFAULT_DB)
	conn = sqlite3.connect(path)
	conn.row_factory = sqlite3.Row
	conn.execute("PRAGMA foreign_keys = ON")
	return conn


def migrate_add_missing_columns(conn: sqlite3.Connection) -> None:
	"""Add missing columns to stamps table if they don't exist (for backwards compat)."""
	cursor = conn.execute("PRAGMA table_info(stamps)")
	existing_cols = {row[1] for row in cursor.fetchall()}
	
	needed = ["country", "year", "face_value", "condition", "catalog_number", "notes", "image_path", "created_at", "updated_at"]
	for col in needed:
		if col not in existing_cols:
			col_type = "TEXT" if col in ["country", "face_value", "condition", "catalog_number", "notes", "image_path", "created_at", "updated_at"] else "INTEGER"
			conn.execute(f"ALTER TABLE stamps ADD COLUMN {col} {col_type}")
	
	# Set created_at and updated_at to current datetime for existing rows
	conn.execute("UPDATE stamps SET created_at = datetime('now') WHERE created_at IS NULL")
	conn.execute("UPDATE stamps SET updated_at = datetime('now') WHERE updated_at IS NULL")
	conn.commit()


def create_tables(conn: sqlite3.Connection) -> None:
	"""Create tables only if they don't exist; separates each CREATE so ALTER works later."""
	statements = [
		"""CREATE TABLE IF NOT EXISTS stamps (
			id INTEGER PRIMARY KEY,
			name TEXT,
			country TEXT,
			year INTEGER,
			face_value TEXT,
			condition TEXT,
			catalog_number TEXT,
			notes TEXT,
			image_path TEXT,
			created_at TEXT DEFAULT (datetime('now')),
			updated_at TEXT DEFAULT (datetime('now'))
		)""",
		"""CREATE TABLE IF NOT EXISTS collections (
			id INTEGER PRIMARY KEY,
			name TEXT NOT NULL,
			owner TEXT,
			description TEXT,
			created_at TEXT DEFAULT (datetime('now'))
		)""",
		"""CREATE TABLE IF NOT EXISTS collection_items (
			id INTEGER PRIMARY KEY,
			collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
			stamp_id INTEGER NOT NULL REFERENCES stamps(id) ON DELETE CASCADE,
			acquisition_date TEXT,
			purchase_price REAL
		)""",
		"""CREATE TABLE IF NOT EXISTS tags (
			id INTEGER PRIMARY KEY,
			name TEXT UNIQUE NOT NULL
		)""",
		"""CREATE TABLE IF NOT EXISTS stamp_tags (
			stamp_id INTEGER NOT NULL REFERENCES stamps(id) ON DELETE CASCADE,
			tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
			PRIMARY KEY (stamp_id, tag_id)
		)""",
		"CREATE INDEX IF NOT EXISTS idx_stamps_country ON stamps(country)",
		"CREATE INDEX IF NOT EXISTS idx_stamps_catalog ON stamps(catalog_number)",
		"CREATE INDEX IF NOT EXISTS idx_collection_items_collection ON collection_items(collection_id)",
	]
	for stmt in statements:
		conn.execute(stmt)
	conn.commit()


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
	if db_path is None:
		DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
	conn = get_connection(db_path)
	
	# Check if stamps table exists first
	cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stamps'")
	stamps_exists = cursor.fetchone() is not None
	
	if stamps_exists:
		# Old DB: migrate columns first before creating indexes
		migrate_add_missing_columns(conn)
	
	create_tables(conn)
	return conn


def add_stamp(conn: sqlite3.Connection, *, name: str, country: Optional[str] = None,
			  year: Optional[int] = None, face_value: Optional[str] = None,
			  condition: Optional[str] = None, catalog_number: Optional[str] = None,
			  notes: Optional[str] = None, image_path: Optional[str] = None) -> int:
	cur = conn.execute(
		"""
		INSERT INTO stamps (name, country, year, face_value, condition, catalog_number, notes, image_path)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		""",
		(name, country, year, face_value, condition, catalog_number, notes, image_path),
	)
	conn.commit()
	return cur.lastrowid


def get_stamp(conn: sqlite3.Connection, stamp_id: int) -> Optional[sqlite3.Row]:
	cur = conn.execute("SELECT * FROM stamps WHERE id = ?", (stamp_id,))
	return cur.fetchone()


def list_stamps(conn: sqlite3.Connection, limit: int = 100) -> List[sqlite3.Row]:
	cur = conn.execute("SELECT * FROM stamps ORDER BY created_at DESC LIMIT ?", (limit,))
	return cur.fetchall()


def find_stamps(conn: sqlite3.Connection, filters: Dict[str, object]) -> List[sqlite3.Row]:
	clauses = []
	params: List[object] = []
	for k, v in filters.items():
		clauses.append(f"{k} = ?")
		params.append(v)
	where = " AND ".join(clauses) if clauses else "1"
	cur = conn.execute(f"SELECT * FROM stamps WHERE {where}", params)
	return cur.fetchall()


def update_stamp(conn: sqlite3.Connection, stamp_id: int, fields: Dict[str, object]) -> None:
	if not fields:
		return
	assignments = ", ".join(f"{k} = ?" for k in fields.keys())
	params = list(fields.values()) + [stamp_id]
	conn.execute(f"UPDATE stamps SET {assignments}, updated_at = datetime('now') WHERE id = ?", params)
	conn.commit()


def delete_stamp(conn: sqlite3.Connection, stamp_id: int) -> None:
	conn.execute("DELETE FROM stamps WHERE id = ?", (stamp_id,))
	conn.commit()


def add_tag(conn: sqlite3.Connection, name: str) -> int:
	cur = conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
	conn.commit()
	if cur.lastrowid:
		return cur.lastrowid
	cur = conn.execute("SELECT id FROM tags WHERE name = ?", (name,))
	row = cur.fetchone()
	return int(row[0])


def tag_stamp(conn: sqlite3.Connection, stamp_id: int, tag_name: str) -> None:
	tag_id = add_tag(conn, tag_name)
	conn.execute("INSERT OR IGNORE INTO stamp_tags (stamp_id, tag_id) VALUES (?, ?)", (stamp_id, tag_id))
	conn.commit()


def close(conn: sqlite3.Connection) -> None:
	conn.close()


if __name__ == "__main__":
	# quick manual smoke test
	c = init_db(":memory:")
	sid = add_stamp(c, name="Blue Penny", country="Mauritius", year=1847, catalog_number="MRT-1")
	print("Inserted stamp id:", sid)
	print(list_stamps(c))
	close(c)

