from contextlib import contextmanager
import json
import mysql.connector
from app.config import db_config

@contextmanager
def connection():
    conn = mysql.connector.connect(**db_config())
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

class Repository:
    def health(self):
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                cur.fetchone()

    def rows(self, query, params=()):
        with connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def locations(self):
        return self.rows('SELECT id, name, x, y FROM locations ORDER BY id')

    def roads(self):
        return self.rows('SELECT id, source_id, target_id, speed_kmph FROM roads ORDER BY id')

    def save_route(self, result):
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO route_history '
                    '(source_id, target_id, mode, path_json, distance_km, duration_minutes) '
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    (result['source_id'], result['target_id'], result['mode'],
                     json.dumps(result['path_ids']), result['distance_km'],
                     result['duration_minutes']))
                history_id = cur.lastrowid
            conn.commit()
            return history_id

    def history(self, limit):
        rows = self.rows('SELECT * FROM route_history ORDER BY id DESC LIMIT %s', (limit,))
        for row in rows:
            row['path_ids'] = json.loads(row.pop('path_json'))
        return rows

def get_repository():
    return Repository()
