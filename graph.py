# graph.py
import heapq
import random

class Graph:
    def __init__(self):
        # adjacency: node -> list of [neighbor, weight, type]
        self.adj = {}
        self.positions_3d = {}  # node -> (x,y,floor)
        self.original_weights = {}  # (a,b) -> w
        self.dynamic_multiplier = 1.0

    # ----------------------------------------------------------------------
    # AGREGAR ARISTA
    # ----------------------------------------------------------------------
    def add_edge(self, a, b, w, edge_type="normal"):
        self.adj.setdefault(a, []).append([b, w, edge_type])
        self.adj.setdefault(b, []).append([a, w, edge_type])
        self.original_weights[(a, b)] = w
        self.original_weights[(b, a)] = w

    # ----------------------------------------------------------------------
    # POSICIONES
    # ----------------------------------------------------------------------
    def set_position(self, node, x, y, floor):
        self.positions_3d[node] = (x, y, floor)

    def nodes(self):
        return list(self.positions_3d.keys())

    # ----------------------------------------------------------------------
    # PESOS DINÁMICOS
    # ----------------------------------------------------------------------
    def set_dynamic_multiplier(self, mult: float):
        self.dynamic_multiplier = max(0.1, float(mult))
        for (a,b), w in self.original_weights.items():
            for edge in self.adj[a]:
                if edge[0] == b:
                    edge[1] = w * self.dynamic_multiplier

    def randomize_congestion(self, extra_min=1, extra_max=8):
        for (a,b), w in self.original_weights.items():
            extra = random.randint(extra_min, extra_max)
            for edge in self.adj[a]:
                if edge[0] == b:
                    edge[1] = (w + extra) * self.dynamic_multiplier

    def restore_original(self):
        for (a,b), w in self.original_weights.items():
            for edge in self.adj[a]:
                if edge[0] == b:
                    edge[1] = w * self.dynamic_multiplier

    # ----------------------------------------------------------------------
    # DIJKSTRA
    # ----------------------------------------------------------------------
    def dijkstra(self, start, end):
        if start not in self.adj or end not in self.adj:
            return float('inf'), []

        dist = {n: float('inf') for n in self.adj}
        prev = {n: None for n in self.adj}
        dist[start] = 0
        pq = [(0, start)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == end:
                break

            for v, w, t in self.adj.get(u, []):  # <-- ahora con 3 valores
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))

        # reconstrucción del camino
        path = []
        node = end
        if prev[node] is None and node != start:
            if dist[end] == float('inf'):
                return float('inf'), []

        while node is not None:
            path.append(node)
            node = prev[node]

        return dist[end], path[::-1]


# =====================================================================
# =============   CONSTRUCCIÓN DEL CASINO COMPLETO  ===================
# =====================================================================

def build_large_casino():
    g = Graph()

    # ==========================================================
    # PISO 1 — ÁREA AMPLIA CON TRAGAMONEDAS Y BARRA
    # ==========================================================
    g.add_edge("L1_Entrada", "L1_Vestibulo", 3, "normal")
    g.add_edge("L1_Vestibulo", "L1_TragamonedasA", 4, "normal")
    g.add_edge("L1_TragamonedasA", "L1_TragamonedasB", 3, "normal")
    g.add_edge("L1_TragamonedasB", "L1_RuletasA", 2, "normal")
    g.add_edge("L1_RuletasA", "L1_Barra", 3, "normal")

    # Ascensor y escaleras piso 1
    g.add_edge("L1_Entrada", "L1_Ascensor", 1, "elevator")
    g.add_edge("L1_TragamonedasA", "L1_Escaleras", 1, "stairs")

    # ==========================================================
    # PISO 2 — VIP, BLACKJACK, PÓKER
    # ==========================================================
    g.add_edge("L2_MesasVIP", "L2_BarraVIP", 3, "normal")
    g.add_edge("L2_BarraVIP", "L2_BlackjackA", 2, "normal")
    g.add_edge("L2_BlackjackA", "L2_BlackjackB", 2, "normal")
    g.add_edge("L2_BlackjackB", "L2_SalaPoker", 3, "normal")
    g.add_edge("L2_SalaPoker", "L2_Pasillo", 3, "normal")

    # Ascensor y escaleras piso 2
    g.add_edge("L2_Ascensor", "L2_MesasVIP", 2, "elevator")
    g.add_edge("L2_Escaleras", "L2_BlackjackA", 2, "stairs")

    # ==========================================================
    # PISO 3 — AUDITORIO, RESTAURANTES
    # ==========================================================
    g.add_edge("L3_Auditorio", "L3_Caja", 3, "normal")
    g.add_edge("L3_Caja", "L3_RestauranteA", 4, "normal")
    g.add_edge("L3_RestauranteA", "L3_RestauranteB", 2, "normal")
    g.add_edge("L3_RestauranteB", "L3_Terraza", 5, "normal")

    # Ascensor y escaleras piso 3
    g.add_edge("L3_Ascensor", "L3_Auditorio", 2, "elevator")
    g.add_edge("L3_Escaleras", "L3_Caja", 2, "stairs")

    # ==========================================================
    # PISO 4 — HOTEL, PENTHOUSE
    g.add_edge("L4_Suites", "L4_Pasarela", 3, "normal")
    g.add_edge("L4_Pasarela", "L4_Penthouse", 4, "normal")

    g.add_edge("L4_Ascensor", "L4_Suites", 1, "elevator")
    g.add_edge("L4_Escaleras", "L4_Suites", 2, "stairs")

    # ==========================================================
    # CONEXIONES VERTICALES (MEJOR SEPARADAS)
    # ==========================================================

    # Ascensor central L1 → L2 → L3 → L4
    g.add_edge("L1_Ascensor", "L2_Ascensor", 2, "elevator")
    g.add_edge("L2_Ascensor", "L3_Ascensor", 2, "elevator")
    g.add_edge("L3_Ascensor", "L4_Ascensor", 2, "elevator")

    # Escaleras lentas L1 → L2 → L3 → L4
    g.add_edge("L1_Escaleras", "L2_Escaleras", 6, "stairs")
    g.add_edge("L2_Escaleras", "L3_Escaleras", 6, "stairs")
    g.add_edge("L3_Escaleras", "L4_Escaleras", 6, "stairs")

    # ==========================================================
    # POSICIONES SEPARADAS (MÁS LIMPIAS Y AMPLIAS)
    # ==========================================================

    coords = {
        # Piso 1
        "L1_Entrada": (1,1,1),
        "L1_Vestibulo": (3,1.5,1),
        "L1_TragamonedasA": (5,2,1),
        "L1_TragamonedasB": (7,2,1),
        "L1_RuletasA": (9,2,1),
        "L1_Barra": (11,1.5,1),
        "L1_Ascensor": (2,4,1),
        "L1_Escaleras": (6,4,1),

        # Piso 2
        "L2_MesasVIP": (1,1,2),
        "L2_BarraVIP": (4,2,2),
        "L2_BlackjackA": (6,2,2),
        "L2_BlackjackB": (8,2.5,2),
        "L2_SalaPoker": (10,1.5,2),
        "L2_Pasillo": (12,1.5,2),
        "L2_Ascensor": (2,4,2),
        "L2_Escaleras": (6,4,2),

        # Piso 3
        "L3_Auditorio": (1,1,3),
        "L3_Caja": (4,2,3),
        "L3_RestauranteA": (6,2,3),
        "L3_RestauranteB": (8,2,3),
        "L3_Terraza": (10,1.5,3),
        "L3_Ascensor": (2,4,3),
        "L3_Escaleras": (6,4,3),

        # Piso 4
        "L4_Suites": (1,1,4),
        "L4_Pasarela": (3.5,2,4),
        "L4_Penthouse": (6,2,4),
        "L4_Ascensor": (2,4,4),
        "L4_Escaleras": (6,4,4)
    }

    for n,(x,y,f) in coords.items():
        g.set_position(n,x,y,f)

    return g
