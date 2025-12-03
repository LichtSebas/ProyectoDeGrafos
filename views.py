# views.py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

# ----------------------------------------
#     VISTA 2D POR PISO
# ----------------------------------------
def figure_floor(graph, floor, highlight_path=None, show_edges=True, show_weights=False):
    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_title(f"Piso {floor} — Grafo (vista 2D)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)

    # Mapea el número de piso (1,2,3,4) al valor Z que usaste en graph.py
    floor_z = {1: 1, 2: 5, 3: 9, 4: 13}
    z = floor_z.get(floor, floor)  # por si acaso
    nodes = [n for n,(x,y,f) in graph.positions_3d.items() if f == z]


    # ---------------------------
    # NODOS
    # ---------------------------
    for node in nodes:
        x,y,_ = graph.positions_3d[node]
        ax.scatter(x, y, s=180, zorder=3, color='skyblue')
        ax.text(x+0.12, y+0.12, node, fontsize=8)

    # ---------------------------
    # ARISTAS EN EL MISMO PISO
    # ---------------------------
    # ---------------------------
    # ARISTAS EN EL MISMO PISO
    # ---------------------------
    if show_edges:
        for node in nodes:
            x, y, _ = graph.positions_3d[node]

            # ahora las aristas tienen 3 valores: neighbor, weight, type
            for neighbor, w, t in graph.adj.get(node, []):
                if neighbor in nodes:

                    # 🔥 evitar duplicar aristas (solo dibujar A→B cuando A < B)
                    if node >= neighbor:
                        continue

                    nx, ny, _ = graph.positions_3d[neighbor]

                    # Escalera/ascensor → línea punteada
                    style = "--" if t in ("stairs", "elevator") else "-"

                    ax.plot([x, nx], [y, ny], style, color='gray', alpha=0.7)

                    if show_weights:
                        mx, my = (x + nx) / 2, (y + ny) / 2
                        ax.text(mx, my, f"{w:.1f}", fontsize=11, color='green')

    # ---------------------------
    # CAMINO RESALTADO
    # ---------------------------
    if highlight_path and len(highlight_path) >= 2:
        for i in range(len(highlight_path)-1):
            a,b = highlight_path[i], highlight_path[i+1]
            if a in nodes and b in nodes:
                x1,y1,_ = graph.positions_3d[a]
                x2,y2,_ = graph.positions_3d[b]
                ax.plot([x1,x2], [y1,y2], color='red', linewidth=3, zorder=5)

    ax.set_aspect('equal', 'box')
    return fig


def figure_mold(graph):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_title("Molde del grafo (solo nodos)")
    ax.grid(True)

    for node,(x,y,f) in graph.positions_3d.items():
        ax.scatter(x, y + (f-1)*0.4, s=100, color='orange')
        ax.text(x+0.12, y+0.12 + (f-1)*0.4, node, fontsize=8)

    ax.set_aspect('equal', 'box')
    return fig


def figure_3d(graph, highlight_path=None, show_weights=False):
    fig = plt.figure(figsize=(8,7))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Mapa 3D del Casino")

    # ---------------------------
    # NODOS 3D
    # ---------------------------
    for node,(x,y,f) in graph.positions_3d.items():
        ax.scatter(x, y, f, s=60, color='skyblue')
        ax.text(x+0.12, y+0.12, f+0.05, node, fontsize=8)

    # ---------------------------
    # ARISTAS 3D
    # ---------------------------
    for u, neighbors in graph.adj.items():
        x1,y1,f1 = graph.positions_3d[u]

        for v,w,t in neighbors:
            x2,y2,f2 = graph.positions_3d[v]
            xs = [x1,x2]
            ys = [y1,y2]
            zs = [f1,f2]

            color = "gray"
            style = ":" if t in ("stairs", "elevator") else "-"

            ax.plot(xs, ys, zs, style, color=color, alpha=0.7)

            if show_weights:
                mx,my,mz = (x1+x2)/2, (y1+y2)/2, (f1+f2)/2
                ax.text(mx, my, mz, f"{w:.1f}", fontsize=11, color='green', fontweight="bold")


    # ---------------------------
    # CAMINO RESALTADO 3D
    # ---------------------------
    if highlight_path and len(highlight_path) >= 2:
        for i in range(len(highlight_path)-1):
            a,b = highlight_path[i], highlight_path[i+1]
            x1,y1,f1 = graph.positions_3d[a]
            x2,y2,f2 = graph.positions_3d[b]
            ax.plot([x1,x2], [y1,y2], [f1,f2], color='red', linewidth=3)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Piso")
    return fig
