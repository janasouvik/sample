import logging
from typing import Annotated, Literal
import mysql.connector
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from app.config import ROOT, traffic_path
from app.db import Repository, get_repository
from app.routing import TrafficError, distance_matrix, find_route, load_traffic
from app.maps import render_map

app = FastAPI(title='Smart Urban Logistics', version='1.0.0',
              description='Learning project: directed routes over synthetic coordinates in km.')
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
Repo = Annotated[Repository, Depends(get_repository)]

class RouteRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source_id: int = Field(gt=0, strict=True)
    target_id: int = Field(gt=0, strict=True)
    mode: Literal['shortest', 'fastest'] = 'shortest'

class RouteResult(RouteRequest):
    path_ids: list[int]
    path_names: list[str]
    distance_km: float
    duration_minutes: float
    history_id: int

@app.exception_handler(mysql.connector.Error)
async def database_error(request: Request, exc):
    logging.getLogger(__name__).error('MySQL request failed (errno=%s)', exc.errno)
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable or incompatible. Check .env, MySQL service and python -m scripts.init_db --check-only.'})

@app.exception_handler(TrafficError)
async def traffic_error(request: Request, exc):
    return JSONResponse(status_code=503, content={'detail': str(exc)})

@app.get('/', include_in_schema=False)
def home():
    return FileResponse(ROOT / 'static' / 'index.html')

@app.get('/health')
def health(repo: Repo):
    repo.health()
    load_traffic(traffic_path())
    return {'status': 'ok', 'database': 'connected', 'traffic': 'readable'}

@app.get('/locations')
def locations(repo: Repo):
    return repo.locations()

@app.get('/roads')
def roads(repo: Repo):
    return repo.roads()

@app.get('/distances')
def distances(repo: Repo):
    places = repo.locations()
    return {'location_ids': [p['id'] for p in places], 'unit': 'km',
            'matrix': distance_matrix(places).round(4).tolist()}

def calculate(repo, source, target, mode):
    try:
        return find_route(repo.locations(), repo.roads(), load_traffic(traffic_path()), source, target, mode)
    except KeyError as exc:
        raise HTTPException(404, 'Source or target location does not exist') from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc

@app.post('/route', response_model=RouteResult, status_code=201)
def route(payload: RouteRequest, repo: Repo):
    result = calculate(repo, payload.source_id, payload.target_id, payload.mode)
    result['history_id'] = repo.save_route(result)
    return result

@app.get('/route-history')
def history(repo: Repo, limit: Annotated[int, Query(ge=1, le=100)] = 20):
    return repo.history(limit)

@app.get('/map', responses={200: {'content': {'image/png': {}}}})
def city_map(repo: Repo,
             source_id: Annotated[int | None, Query(gt=0)] = None,
             target_id: Annotated[int | None, Query(gt=0)] = None,
             mode: Literal['shortest', 'fastest'] = 'shortest'):
    if (source_id is None) != (target_id is None):
        raise HTTPException(422, 'Provide both source_id and target_id, or neither')
    places, links = repo.locations(), repo.roads()
    path = []
    if source_id is not None:
        try:
            path = find_route(places, links, load_traffic(traffic_path()), source_id, target_id, mode)['path_ids']
        except (KeyError, LookupError) as exc:
            raise HTTPException(404, 'Unknown location or no route') from exc
    return Response(render_map(places, links, path), media_type='image/png',
                    headers={'Cache-Control': 'no-store'})
