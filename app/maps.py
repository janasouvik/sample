"""Headless Matplotlib map. A lock serializes Matplotlib access across requests."""
from io import BytesIO
from threading import Lock
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

LOCK = Lock()

def render_map(locations, roads, path=()):
    with LOCK:
        points = {p['id']: p for p in locations}
        fig = Figure(figsize=(9, 5.5), layout='constrained')
        ax = fig.subplots()
        for road in roads:
            a, b = points[road['source_id']], points[road['target_id']]
            ax.annotate('', xy=(b['x'], b['y']), xytext=(a['x'], a['y']),
                        arrowprops=dict(arrowstyle='->', color='#bac5d2', lw=1.5))
        for a_id, b_id in zip(path, path[1:]):
            a, b = points[a_id], points[b_id]
            ax.plot([a['x'], b['x']], [a['y'], b['y']], color='#147d63', lw=4)
        for p in locations:
            ax.scatter(p['x'], p['y'], s=90, color='#163c63', zorder=3)
            ax.annotate(p['name'], (p['x'], p['y']), xytext=(5, 8), textcoords='offset points')
        ax.set(title='Bengaluru | teaching network (not to scale)', xlabel='X (km)', ylabel='Y (km)')
        ax.set_aspect('equal', adjustable='datalim')
        ax.margins(0.2)
        ax.grid(alpha=0.15)
        output = BytesIO()
        fig.savefig(output, format='png', dpi=130)
        fig.clear()
        return output.getvalue()
