import os
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "app.db")

class DB:
    def __init__(self):
        self.path = DB_PATH

    def init(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with sqlite3.connect(self.path) as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                rep_id TEXT NOT NULL,
                question TEXT NOT NULL,
                intent TEXT NOT NULL,
                reformulated_query TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                agent_mode TEXT NOT NULL
            );
            """)
            con.commit()

    def log_interaction(self, rep_id: str, question: str, intent: str, reformulated_query: str, answer: str, sources: str, confidence: int, latency_ms: int, agent_mode: str):
        with sqlite3.connect(self.path) as con:
            con.execute("""
                INSERT INTO interactions (ts, rep_id, question, intent, reformulated_query, answer, sources, confidence, latency_ms, agent_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.utcnow().isoformat(), rep_id, question, intent, reformulated_query, answer, sources, confidence, latency_ms, agent_mode))
            con.commit()

    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.path) as con:
            con.row_factory = sqlite3.Row

            total = con.execute("SELECT COUNT(*) as n FROM interactions").fetchone()["n"]
            avg_conf = con.execute("SELECT AVG(confidence) as v FROM interactions").fetchone()["v"]
            avg_lat = con.execute("SELECT AVG(latency_ms) as v FROM interactions").fetchone()["v"]

            per_rep = con.execute("""
                SELECT rep_id, COUNT(*) as queries, AVG(confidence) as avg_conf
                FROM interactions
                GROUP BY rep_id
                ORDER BY queries DESC
            """).fetchall()

            top_intents = con.execute("""
                SELECT intent, COUNT(*) as cnt
                FROM interactions
                GROUP BY intent
                ORDER BY cnt DESC
                LIMIT 10
            """).fetchall()

            top_docs = con.execute("""
                SELECT sources, COUNT(*) as cnt
                FROM interactions
                GROUP BY sources
                ORDER BY cnt DESC
                LIMIT 10
            """).fetchall()

            low_conf = con.execute("""
                SELECT ts, rep_id, intent, confidence, sources
                FROM interactions
                WHERE confidence < 60
                ORDER BY ts DESC
                LIMIT 20
            """).fetchall()

        def rows_to_list(rows):
            return [dict(r) for r in rows]

        return {
            "total_queries": total,
            "avg_confidence": round(avg_conf or 0, 2),
            "avg_latency_ms": round(avg_lat or 0, 2),
            "per_rep": rows_to_list(per_rep),
            "top_intents": rows_to_list(top_intents),
            "top_docs": rows_to_list(top_docs),
            "low_confidence": rows_to_list(low_conf),
        }
