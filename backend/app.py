from flask import Flask, request, jsonify
from flask_cors import CORS

import psycopg2
import os
import sys
import logging

# ── Logging setup ──────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

# ── Flask app ──────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ── Database connection ──────────────────────────────
logger.info("Connecting to DB with:")
logger.info(f"  DB_HOST={os.getenv('DB_HOST')}")
logger.info(f"  DB_NAME={os.getenv('DB_NAME')}")
logger.info(f"  DB_USER={os.getenv('DB_USER')}")
logger.info(f"  DB_PASS={os.getenv('DB_PASS')}")

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )
    cursor = conn.cursor()
    logger.info("Connected to PostgreSQL")

    # Create tasks table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """
    )
    conn.commit()
    logger.info("Ensured tasks table exists")

except Exception as e:
    logger.error("Failed to connect to the database", exc_info=True)
    sys.exit(1)


# ── Routes ───────────────────────────────
@app.route("/")
def health():
    logger.info("Health check")
    return "Server is up"


@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        cursor.execute("SELECT id, text, done FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        tasks = [{"id": r[0], "text": r[1], "done": r[2]} for r in rows]
        return jsonify(tasks)
    except Exception as e:
        logger.error("Error fetching tasks", exc_info=True)
        return jsonify({"error": "Failed to fetch tasks"}), 500


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    if not data or "text" not in data:
        logger.warning("POST /tasks missing 'text'")
        return jsonify({"error": "Missing 'text' in request body"}), 400
    try:
        cursor.execute("INSERT INTO tasks (text) VALUES (%s) RETURNING id, text, done", (data["text"],))
        task = cursor.fetchone()
        conn.commit()
        if task:
            logger.info(f"Task added: {task}")
            return jsonify({"id": task[0], "text": task[1], "done": task[2]}), 201
        else:
            logger.error("No task returned from DB after insert")
            return jsonify({"error": "Failed to create task"}), 500
    except Exception as e:
        logger.error("Error adding task", exc_info=True)
        return jsonify({"error": "Failed to add task"}), 500


@app.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    try:
        cursor.execute("UPDATE tasks SET done = TRUE WHERE id = %s RETURNING id, text, done", (task_id,))
        task = cursor.fetchone()
        conn.commit()
        if task:
            logger.info(f"Task marked complete: {task_id}")
            return jsonify({"id": task[0], "text": task[1], "done": task[2]})
        else:
            logger.warning(f"Task not found for completion: {task_id}")
            return jsonify({"error": "Not found"}), 404
    except Exception as e:
        logger.error("Error completing task", exc_info=True)
        return jsonify({"error": "Failed to complete task"}), 500


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        logger.info(f"Task deleted: {task_id}")
        return "", 204
    except Exception as e:
        logger.error("Error deleting task", exc_info=True)
        return jsonify({"error": "Failed to delete task"}), 500


# ── Run ───────────────────────────────
if __name__ == "__main__":
    logger.info("Starting Flask server")
app.run(host="0.0.0.0", port=5000)
