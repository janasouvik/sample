"""Preflight first; never migrate an existing table automatically."""
import argparse
import sys
import mysql.connector
from app.config import ROOT
from app.db import connection

EXPECTED = {
    'locations': {'id': 'int', 'name': 'varchar', 'x': 'double', 'y': 'double'},
    'roads': {'id': 'int', 'source_id': 'int', 'target_id': 'int', 'speed_kmph': 'double'},
    'route_history': {'id': 'int', 'source_id': 'int', 'target_id': 'int', 'mode': 'enum',
                      'path_json': 'json', 'distance_km': 'double', 'duration_minutes': 'double',
                      'created_at': 'timestamp'}}

def preflight(conn, allow_missing=False):
    problems = []
    with conn.cursor(dictionary=True) as cur:
        for table, required in EXPECTED.items():
            cur.execute('SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA '
                        'FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s', (table,))
            rows = {r['COLUMN_NAME']: r for r in cur.fetchall()}
            if not rows:
                if not allow_missing:
                    problems.append(f'{table}: missing table; run initializer')
                continue
            for name, dtype in required.items():
                if name not in rows or rows[name]['DATA_TYPE'] != dtype:
                    problems.append(f'{table}.{name}: expected {dtype}')
            for name, row in rows.items():
                if name not in required and row['IS_NULLABLE'] == 'NO' and row['COLUMN_DEFAULT'] is None and 'auto_increment' not in row['EXTRA'] and 'GENERATED' not in row['EXTRA']:
                    problems.append(f'{table}.{name}: extra required column')
            if 'id' in rows and 'auto_increment' not in rows['id']['EXTRA']:
                problems.append(f'{table}.id must be AUTO_INCREMENT')
            if table == 'locations' and 'name' in rows:
                import re
                length = re.search(r'varchar\((\d+)\)', rows['name']['COLUMN_TYPE'])
                if not length or int(length[1]) < 100:
                    problems.append('locations.name must support at least 100 characters')
            if table == 'route_history':
                if 'mode' in rows and rows['mode']['COLUMN_TYPE'] != "enum('shortest','fastest')":
                    problems.append('route_history.mode enum must contain shortest,fastest in that order')
                if 'created_at' in rows and 'CURRENT_TIMESTAMP' not in str(rows['created_at']['COLUMN_DEFAULT']).upper():
                    problems.append('route_history.created_at needs DEFAULT CURRENT_TIMESTAMP')
            cur.execute('SHOW INDEX FROM `' + table + '`')
            indexes = {}
            for idx in cur.fetchall():
                if idx['Non_unique'] == 0 and idx.get('Sub_part') is None:
                    indexes.setdefault(idx['Key_name'], []).append((idx['Seq_in_index'], idx['Column_name']))
            uniques = [tuple(col for _, col in sorted(parts)) for parts in indexes.values()]
            if ('id',) not in uniques:
                problems.append(f'{table}: id must be unique')
            needed = ('name',) if table == 'locations' else ('source_id', 'target_id') if table == 'roads' else None
            if needed and needed not in uniques:
                problems.append(f'{table}: unique key required on {needed}')
            cur.execute('SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s', (table,))
            if cur.fetchone()['ENGINE'] != 'InnoDB':
                problems.append(f'{table}: InnoDB required')
    if problems:
        raise ValueError('Schema mismatch; no automatic migration.\n- ' + '\n- '.join(problems))

def execute_file(conn, path):
    # Bundled SQL has no procedures or semicolons inside string literals.
    text = '\n'.join(line for line in path.read_text(encoding='utf-8').splitlines() if not line.lstrip().startswith('--'))
    with conn.cursor() as cur:
        for statement in text.split(';'):
            if statement.strip():
                cur.execute(statement)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Read schema only; no writes')
    args = parser.parse_args()
    try:
        with connection() as conn:
            preflight(conn, allow_missing=not args.check_only)
            if not args.check_only:
                execute_file(conn, ROOT / 'sql/schema.sql')
                preflight(conn)
                execute_file(conn, ROOT / 'sql/seed.sql')
                conn.commit()
            print('Schema compatible.' if args.check_only else 'Schema and demo seed ready. Existing rows preserved.')
    except (mysql.connector.Error, ValueError) as exc:
        if isinstance(exc, mysql.connector.Error):
            print(f'Database setup failed (MySQL errno {exc.errno}). Check service, database, permissions and .env.', file=sys.stderr)
        else:
            print(str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
