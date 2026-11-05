# Bengaluru Edition

Real Bengaluru names; synthetic coordinates, graph, speeds, and traffic. Results are teaching examples, not real road distances, journey times, or Metro routes. Whitefield has no edges in this small sample; this does not mean it is disconnected in the real city. Use the `smart_logistics_bengaluru` database to avoid mixing datasets.

# Smart Urban Logistics — Beginner FastAPI Project

A complete local learning project for finding delivery routes using a MySQL database named **smart_logistics_bengaluru**. Extract the ZIP or clone the repository before running anything. Open the `smart-urban-logistics` folder in VS Code, then open its terminal. All commands below run from that folder unless stated otherwise.

---

## Aim and What You Will Learn

Build an end-to-end route planner:
1. **Database Integration**: Read road networks and locations from MySQL using `mysql-connector-python`.
2. **Matrix Calculations**: Calculate straight-line distances using NumPy vector mathematics.
3. **Data Analysis**: Apply simulated traffic delay multipliers from a pandas CSV (`data/traffic.csv`).
4. **Graph Algorithms**: Execute Dijkstra's algorithm for **shortest distance** or **fastest travel time**.
5. **Data Visualization**: Dynamically render delivery route maps with Matplotlib.
6. **Persistence**: Save route logs in MySQL `route_history`.
7. **Frontend & API**: An interactive HTML5/CSS/JavaScript interface calling FastAPI endpoints.

No paid service, map API key, or internet connection is needed at runtime.

---

## Stack and Prerequisites

- **OS**: Windows 10/11
- **Python**: Python **3.14 x64** recommended (compatible with 3.10+).
- **Database**: MySQL Server **8.0+** or **8.4** and MySQL Workbench (the MySQL Server Windows service must be running).
- **Core Libraries**: FastAPI, Uvicorn, mysql-connector-python, NumPy, pandas, Matplotlib, python-dotenv.
- **Tools**: VS Code + Python extension, any modern browser, and optionally Postman.

---

## 1. Start or Stop MySQL (Administrator Terminal)

Starting or stopping Windows services requires an Administrator terminal. Normal project commands do not.

### Start the Service:
**CMD (Administrator):**
```bat
net start MySQL80
```

**PowerShell (Administrator):**
```powershell
Start-Service -Name MySQL80
```
*(If your service is named `MySQL84` or another name, substitute that instead).*

### Stop the Service (when done):
**CMD (Administrator):**
```bat
net stop MySQL80
```

**PowerShell (Administrator):**
```powershell
Stop-Service -Name MySQL80
```

---

## 2. Create the Python Virtual Environment & Install Dependencies

Open a standard (non-admin) terminal in the project folder.

### Command Prompt (CMD):
```bat
py -3.14 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

### PowerShell:
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

---

## 3. Configure Database Credentials (.env)

Open `.env` in VS Code or Notepad and configure your local MySQL credentials:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=smart_logistics_bengaluru
DB_USER=root
DB_PASSWORD="your_actual_mysql_password"
TRAFFIC_CSV=data/traffic.csv
```

> **Note:**
> - Keep quotes around the password if it contains `#`, `@`, or spaces.
> - Never commit `.env` to GitHub. `.env.example` is provided as a safe template.

If you haven't created the database yet, run this in MySQL Workbench or the MySQL command line:
```sql
CREATE DATABASE IF NOT EXISTS smart_logistics_bengaluru CHARACTER SET utf8mb4;
```

---

## 4. Database Schema, Migrations & Seeding

This project requires three tables in your database:
1. `locations`: Stores Bengaluru hubs and synthetic Cartesian (X, Y) coordinates.
2. `roads`: Stores directed edges between locations with speed limits (`speed_kmph`).
3. `route_history`: Stores audit logs of calculated routes with timestamps and JSON paths.

You can set up the tables and seed data using either the **Automated Python Runner** or **Direct SQL Execution**.

### Method A: Automated Python Migration & Seed Runner (Recommended)

The project includes an intelligent migration runner [`scripts/init_db.py`](scripts/init_db.py) that performs pre-flight validation and ensures existing data is never corrupted or deleted.

#### Step 1: Pre-flight Verification (Read-Only)
Check whether your database is reachable and verify schema compatibility without writing any data:

**CMD:**
```bat
python -m scripts.init_db --check-only
```

**PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m scripts.init_db --check-only
```

#### Step 2: Apply Migrations & Seed Data
Creates missing tables (`sql/schema.sql`) and populates the default 6 Bengaluru locations and 10 directed roads (`sql/seed.sql`):

**CMD:**
```bat
python -m scripts.init_db
```

**PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m scripts.init_db
```

**Output:**
```
Schema and demo seed ready. Existing rows preserved.
```

---

### Method B: Manual SQL Execution (MySQL Workbench or CLI)

If you prefer to run raw SQL scripts directly:

#### In MySQL Workbench:
1. Connect to your MySQL server.
2. Ensure database exists:
   ```sql
   USE smart_logistics_bengaluru;
   ```
3. Open and run [`sql/schema.sql`](sql/schema.sql) (creates tables with indexes, foreign keys, and constraints).
4. Open and run [`sql/seed.sql`](sql/seed.sql) (populates initial locations and roads safely using `WHERE NOT EXISTS`).

#### Via MySQL Command Line:
**CMD:**
```bat
mysql -h 127.0.0.1 -u root -p smart_logistics_bengaluru < sql\schema.sql
mysql -h 127.0.0.1 -u root -p smart_logistics_bengaluru < sql\seed.sql
```

### Seed Data Summary:
- **Locations**:
  - `Majestic` (0, 0)
  - `Vidhana Soudha` (2, 0)
  - `Cubbon Park` (0, 3)
  - `MG Road` (4, 0)
  - `Indiranagar` (6, 0)
  - `Whitefield` (8, 3 — intentionally disconnected for unreachable route demonstration)
- **Road Network**: 10 directed connections with base speeds (30 km/h to 60 km/h).

---

## 5. Start FastAPI & Launch the Web Application

### Command Prompt (CMD):
```bat
scripts\start.cmd
```

### PowerShell:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Keep the terminal window running. Open your browser:

- **Frontend User Interface**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Service Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 6. How Route Planning Works

```text
Browser / Postman ──> FastAPI Endpoint (POST /route)
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
  MySQL Database                          traffic.csv
  (locations & roads)                 (delay multipliers)
       │                                       │
       └───────────────────┬───────────────────┘
                           ▼
              NumPy Matrix Calculations
                           ▼
          Dijkstra Graph Search (Shortest vs. Fastest)
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
Saved to MySQL (route_history)         Dynamic Matplotlib PNG
```

### Dijkstra Modes:
- **`shortest`**: Minimizes total physical distance ($km$) along valid road segments.
  - Example: `Majestic` $\rightarrow$ `Vidhana Soudha` $\rightarrow$ `MG Road` (4.0 km, but heavy traffic takes 24 min).
- **`fastest`**: Minimizes total journey duration ($minutes$) by incorporating traffic factors:
  $$\text{travel\_minutes} = \frac{\text{distance\_km}}{\text{speed\_kmph}} \times 60 \times \text{traffic\_multiplier}$$
  - Example: `Majestic` $\rightarrow$ `Cubbon Park` $\rightarrow$ `MG Road` (8.0 km detour, but free-flowing road takes only 8 min).

### Dynamic Traffic Delays:
Edit [`data/traffic.csv`](data/traffic.csv) at any time. Changes take effect on the next request without needing to restart the server!
Format:
```csv
source,target,multiplier
Majestic,Vidhana Soudha,3.0
Vidhana Soudha,MG Road,3.0
```

---

## 7. API Endpoints & Request Examples

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI Route Planner |
| `GET` | `/health` | Verifies MySQL connection and CSV access |
| `GET` | `/locations` | Lists all locations with IDs and X/Y coordinates |
| `GET` | `/roads` | Lists all directed road segments and speed limits |
| `GET` | `/distances` | NumPy-computed all-pairs Euclidean distance matrix |
| `POST` | `/route` | Computes route, returns JSON, and logs to `route_history` |
| `GET` | `/route-history?limit=20` | Returns latest saved routes from database |
| `GET` | `/map` | Returns static network diagram as PNG image |
| `GET` | `/map?source_id=1&target_id=4&mode=fastest` | Returns route highlighted in green |
| `GET` | `/docs` | Swagger interactive OpenAPI documentation |

### Example Request (`POST /route`):
```json
{
  "source_id": 1,
  "target_id": 4,
  "mode": "fastest"
}
```

### Example Response (`201 Created`):
```json
{
  "source_id": 1,
  "target_id": 4,
  "mode": "fastest",
  "path_ids": [1, 3, 4],
  "path_names": ["Majestic", "Cubbon Park", "MG Road"],
  "distance_km": 8.0,
  "duration_minutes": 8.0,
  "history_id": 1
}
```

---

## 8. Testing the Application (Manual & Postman)

### Step-by-Step Verification Checklist:
1. **Health Check**: Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) — should return `{"status": "ok", "database": "connected", "traffic_csv": "ok"}`.
2. **Retrieve Locations**: Open [http://127.0.0.1:8000/locations](http://127.0.0.1:8000/locations) to confirm seeded IDs.
3. **Plan in Browser**:
   - Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Select **Majestic** $\rightarrow$ **MG Road** with mode **Shortest**.
   - Note the result (4.0 km, 24.0 min).
   - Change mode to **Fastest** and recalculate.
   - Note the result (8.0 km, 8.0 min).
4. **Inspect Route History**: Open [http://127.0.0.1:8000/route-history](http://127.0.0.1:8000/route-history) to see the recorded entries.
5. **Disconnected Node Test**: Select **Majestic** $\rightarrow$ **Whitefield** — should return error 404 (no route exists).

### Postman Testing:
1. Import `postman/Smart_Urban_Logistics.postman_collection.json` into Postman.
2. Collection variable `base_url` defaults to `http://127.0.0.1:8000`.
3. Run **Locations (capture demo IDs)** first, then test the POST route requests.

---

## 9. Stopping and Restarting

- To stop FastAPI: Press **Ctrl+C** in the terminal running Uvicorn.
- To restart FastAPI: Re-run the start command.
- To deactivate the Python environment in CMD: Run `deactivate`.

If port 8000 is reported busy:
- Find and terminate the previous process:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000 -State Listen
  ```
- Or run on a different port:
  ```powershell
  .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
  ```

---

## 10. Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| **503 Database Unavailable** | MySQL service not running | Run `net start MySQL80` in Admin terminal |
| **Error 1045 Access Denied** | Wrong password or user in `.env` | Verify `.env` credentials, quote passwords with special characters |
| **Error 1049 Unknown Database** | Database not created | Run `CREATE DATABASE smart_logistics_bengaluru;` in MySQL Workbench |
| **Schema Mismatch Error** | Missing tables or columns | Run `python -m scripts.init_db` to create missing tables and seed data |
| **CSV Error** | Missing or corrupted `data/traffic.csv` | Restore default header `source,target,multiplier` and non-negative values |
| **ModuleNotFoundError** | Dependencies installed globally, not in venv | Activate `.venv` or run via `.\.venv\Scripts\python.exe` |

---

## 11. Project Directory Structure

```text
smart-urban-logistics-bengaluru/
├── app/
│   ├── __init__.py
│   ├── config.py         # .env loading and file path resolution
│   ├── db.py             # MySQL queries and transaction handling
│   ├── main.py           # FastAPI endpoints and route handlers
│   ├── maps.py           # Matplotlib PNG graph visualization
│   └── routing.py        # NumPy distances and Dijkstra algorithm
├── data/
│   └── traffic.csv       # Editable traffic congestion multipliers
├── docs/
│   └── fastest-route-example.png
├── examples/
│   ├── route-fastest.json
│   └── route-shortest.json
├── postman/
│   └── Smart_Urban_Logistics.postman_collection.json
├── scripts/
│   ├── __init__.py
│   ├── init_db.py        # Pre-flight check, schema migration & seed runner
│   ├── start.cmd         # Windows CMD starter script
│   └── start.ps1         # Windows PowerShell starter script
├── sql/
│   ├── schema.sql        # Table definitions (locations, roads, route_history)
│   └── seed.sql          # Sample Bengaluru locations and roads
├── static/
│   ├── app.js            # Frontend JavaScript
│   ├── index.html        # Web interface
│   └── style.css         # UI styles
├── .env.example          # Template for database configuration
├── .gitignore            # Git exclusions (.env, .venv, caches)
├── README.md             # Complete project guide
├── requirements.txt      # Production runtime dependencies
└── START_HERE.txt        # Student quickstart walkthrough
```
