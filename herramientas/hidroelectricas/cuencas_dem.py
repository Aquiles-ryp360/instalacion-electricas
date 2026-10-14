"""Delimitación exploratoria D8. No sustituye un DEM hidrológicamente validado."""
import heapq
from collections import deque
import numpy as np


def drenaje_d8(elevacion, dx_m, dy_m):
    """Rellena depresiones por priority flood, dirige D8 y acumula celdas.

    Los empates en zonas planas usan el árbol de salida del relleno. Cada celda
    tiene a lo sumo un receptor. Los bordes son salidas abiertas. Distancias en m.
    Devuelve relleno, receptor (índice plano, -1 en borde) y acumulación en celdas.
    """
    z = np.asarray(elevacion, dtype=float)
    if z.ndim != 2 or min(z.shape) < 3 or not np.isfinite(z).all():
        raise ValueError('DEM debe ser una matriz finita de al menos 3 por 3')
    if min(dx_m, dy_m) <= 0:
        raise ValueError('Resolución debe ser positiva')
    nr, nc = z.shape
    filled = z.copy()
    seen = np.zeros(z.shape, bool)
    parent = np.full(z.size, -1, dtype=np.int64)
    rank = np.full(z.size, -1, dtype=np.int64)
    heap = []
    for r in range(nr):
        for c in range(nc):
            if r in (0, nr - 1) or c in (0, nc - 1):
                seen[r, c] = True
                heapq.heappush(heap, (z[r, c], r * nc + c))
    offsets = [(dr, dc, np.hypot(dr * dy_m, dc * dx_m))
               for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
    counter = 0
    while heap:
        height, idx = heapq.heappop(heap)
        rank[idx] = counter
        counter += 1
        r, c = divmod(idx, nc)
        for dr, dc, _ in offsets:
            rr, cc = r + dr, c + dc
            if 0 <= rr < nr and 0 <= cc < nc and not seen[rr, cc]:
                seen[rr, cc] = True
                new_height = max(height, z[rr, cc])
                filled[rr, cc] = new_height
                parent[rr * nc + cc] = idx
                heapq.heappush(heap, (new_height, rr * nc + cc))
    receiver = parent.copy()
    for r in range(1, nr - 1):
        for c in range(1, nc - 1):
            idx = r * nc + c
            best = 0.0
            for dr, dc, distance in offsets:
                slope = (filled[r, c] - filled[r + dr, c + dc]) / distance
                if slope > best:
                    best = slope
                    receiver[idx] = (r + dr) * nc + c + dc
    indegree = np.zeros(z.size, dtype=np.int64)
    np.add.at(indegree, receiver[receiver >= 0], 1)
    queue = deque(np.flatnonzero(indegree == 0).tolist())
    accumulation = np.ones(z.size, dtype=np.int64)
    visited = 0
    while queue:
        idx = queue.popleft()
        visited += 1
        nxt = receiver[idx]
        if nxt >= 0:
            accumulation[nxt] += accumulation[idx]
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(int(nxt))
    if visited != z.size:
        raise ArithmeticError('La red D8 contiene un ciclo')
    if int(accumulation[receiver < 0].sum()) != z.size:
        raise ArithmeticError('No se conserva el número de celdas')
    return filled, receiver.reshape(z.shape), accumulation.reshape(z.shape)


def cuenca_receptora(receiver, outlet_index):
    """Máscara de todas las celdas que drenan al punto indicado, incluida esa celda."""
    recv = np.asarray(receiver, dtype=np.int64)
    if not 0 <= outlet_index < recv.size:
        raise ValueError('Salida fuera del DEM')
    upstream = [[] for _ in range(recv.size)]
    for i, nxt in enumerate(recv.ravel()):
        if nxt >= 0:
            upstream[int(nxt)].append(i)
    selected = np.zeros(recv.size, bool)
    stack = [int(outlet_index)]
    while stack:
        idx = stack.pop()
        if selected[idx]:
            raise ArithmeticError('Ciclo en receptores')
        selected[idx] = True
        stack.extend(upstream[idx])
    return selected.reshape(recv.shape)
