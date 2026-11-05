import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False)

def db_config():
    return dict(host=os.getenv('DB_HOST', '127.0.0.1'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER', 'smart_app'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'smart_logistics_bengaluru'),
                connection_timeout=5, autocommit=False)

def traffic_path():
    value = Path(os.getenv('TRAFFIC_CSV', 'data/traffic.csv'))
    return value if value.is_absolute() else ROOT / value
