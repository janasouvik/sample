"""Directed graph, NumPy Euclidean distances, pandas traffic and heap Dijkstra."""
import heapq
import math
import numpy as np
import pandas as pd

class TrafficError(ValueError):
    pass

def load_traffic(path):
    try:
        frame = pd.read_csv(path, keep_default_na=False)
        if not {'source', 'target', 'multiplier'} <= set(frame.columns):
            raise ValueError('Required columns: source,target,multiplier')
        if frame.duplicated(['source', 'target']).any():
            raise ValueError('Duplicate directed traffic pair')
        result = {}
        for row in frame.itertuples(index=False):
            factor = float(row.multiplier)
            if not math.isfinite(factor) or factor < 1:
                raise ValueError('Traffic multipliers must be finite and >= 1')
            if not str(row.source).strip() or not str(row.target).strip():
                raise ValueError('Traffic names cannot be empty')
            result[(str(row.source), str(row.target))] = factor
        return result
    except (OSError, ValueError, TypeError, pd.errors.ParserError) as exc:
        raise TrafficError('Cannot read traffic.csv. Check its header, pairs and multipliers.') from exc

def distance_matrix(locations):
    xy = np.array([[float(p['x']), float(p['y'])] for p in locations], dtype=float).reshape(-1, 2)
    if not np.isfinite(xy).all():
        raise ValueError('Location coordinates must be finite')
    delta = xy[:, None, :] - xy[None, :, :]
    return np.sqrt(np.sum(delta * delta, axis=2))

def graph_data(locations, roads, traffic):
    index = {p['id']: i for i, p in enumerate(locations)}
    names = {p['id']: p['name'] for p in locations}
    distances = distance_matrix(locations)
    graph = {p['id']: [] for p in locations}
    for road in roads:
        a, b = road['source_id'], road['target_id']
        speed = float(road['speed_kmph'])
        if a not in index or b not in index or not math.isfinite(speed) or speed <= 0:
            raise ValueError('Road endpoints or speed are invalid')
        distance = float(distances[index[a], index[b]])
        factor = traffic.get((names[a], names[b]), 1.0)
        minutes = distance / speed * 60 * factor
        graph[a].append((b, distance, minutes))
    return graph

def find_route(locations, roads, traffic, source, target, mode):
    if mode not in ('shortest', 'fastest'):
        raise ValueError('Unknown route mode')
    graph = graph_data(locations, roads, traffic)
    if source not in graph or target not in graph:
        raise KeyError('Unknown location ID')
    best, previous, queue = {source: 0.0}, {}, [(0.0, source)]
    while queue:
        cost, current = heapq.heappop(queue)
        if cost > best[current]:
            continue
        if current == target:
            break
        for neighbor, distance, minutes in graph[current]:
            next_cost = cost + (distance if mode == 'shortest' else minutes)
            if next_cost < best.get(neighbor, math.inf):
                best[neighbor] = next_cost
                previous[neighbor] = (current, distance, minutes)
                heapq.heappush(queue, (next_cost, neighbor))
    if target not in best:
        raise LookupError('No directed road path connects these locations')
    path, distance, minutes = [target], 0.0, 0.0
    while path[-1] != source:
        parent, d, t = previous[path[-1]]
        path.append(parent)
        distance += d
        minutes += t
    path.reverse()
    names = {p['id']: p['name'] for p in locations}
    return dict(source_id=source, target_id=target, mode=mode, path_ids=path,
                path_names=[names[i] for i in path], distance_km=round(distance, 4),
                duration_minutes=round(minutes, 4))
