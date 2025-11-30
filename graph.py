# graph.py
import heapq
import random
import networkx as nx

class Graph:
    def __init__(self):
        # adjacency: node -> list of [neighbor, weight, type]
        self.adj = {}
        self.positions_3d = {}  # node -> (x,y,floor)
        self.original_weights = {}  # (a,b) -> w
        self.dynamic_multiplier = 1.0
        self.congestion_zones = {}




    def set_zone_congestion(self, node_or_edge, factor):
        """
        node_or_edge: str o tuple(a,b)
        factor: multiplicador adicional (1.0 = sin cambio, >1 = más pesado)
        """
        self.congestion_zones[node_or_edge] = factor
        self.apply_congestion()

    def apply_congestion(self):
        # Reaplicar pesos dinámicos con zonas de congestión
        for (a,b), w in self.original_weights.items():
            multiplier = self.dynamic_multiplier
            # revisar si a o b tienen congestión por zona
            multiplier *= self.congestion_zones.get(a, 1.0)
            multiplier *= self.congestion_zones.get(b, 1.0)
            # revisar si la arista (a,b) tiene factor de congestión específico
            multiplier *= self.congestion_zones.get((a,b), 1.0)
            for edge in self.adj[a]:
                if edge[0] == b:
                    edge[1] = w * multiplier
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
    def randomize_specific_congestion(self, nodes):
        for node in nodes:
            factor = random.uniform(1.5, 3.0)  # congestión aleatoria
            self.graph.set_zone_congestion(node, factor)

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
    def set_edge_weight(self, a, b, new_weight):
        # actualizar arista a -> b
        for edge in self.adj[a]:
            if edge[0] == b:
                edge[1] = new_weight
        # actualizar arista b -> a
        for edge in self.adj[b]:
            if edge[0] == a:
                edge[1] = new_weight

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

    # Cruces Piso 1 (Tragamonedas ↔ Barra)
    g.add_edge("L1_TragamonedasA", "L1_Barra", 5, "normal")  # ruta diagonal

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

    # Cruces Piso 2 (VIP ↔ Blackjack)
    g.add_edge("L2_BarraVIP", "L2_BlackjackB", 3, "normal")
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

    # Cruces Piso 3 (Auditorio ↔ Restaurante B)
    g.add_edge("L3_Auditorio", "L3_RestauranteB", 6, "normal")

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

    # Nodo de cruce intermedio
    g.set_position("Nodo_Central1", 5, 3, 1)
    g.add_edge("L1_TragamonedasB", "Nodo_Central1", 2, "normal")
    g.add_edge("L1_Barra", "Nodo_Central1", 2, "normal")
    g.add_edge("L1_Escaleras", "L2_MesasVIP", 5, "stairs")  # ruta alternativa más corta
    g.add_edge("L2_Escaleras", "L3_Caja", 4, "stairs")      # otro cruce

    # ==========================================================
    # CONEXIONES NUEVAS (CONEXION DE NODOS YA EXISTENTES)
    # ==========================================================
    g.add_edge("L1_Ascensor", "L1_Escaleras", 2, "normal")  # nueva conexión piso 1
    g.add_edge("L1_Ascensor", "L1_TragamonedasB", 3, "normal")  # opcional atajo
    g.add_edge("L2_Ascensor", "L2_Escaleras", 2, "normal")
    g.add_edge("L2_Ascensor", "L2_BlackjackB", 3, "normal")  # cruce adicional
    g.add_edge("L3_Ascensor", "L3_Escaleras", 2, "normal")
    g.add_edge("L3_Ascensor", "L3_RestauranteB", 3, "normal")  # cruce diagonal
    # rutas alternativas verticales
    g.add_edge("L1_Ascensor", "L2_Escaleras", 4, "stairs")  
    g.add_edge("L2_Ascensor", "L3_Escaleras", 4, "stairs")  

    # ==========================================================
    # POSICIONES SEPARADAS (MÁS LIMPIAS Y AMPLIAS)
    # ==========================================================

    coords = {
        # Piso 1
        "L1_Entrada": (1, 1, 1),
        "L1_Vestibulo": (4, 2, 1),
        "L1_TragamonedasA": (7, 3, 1),
        "L1_TragamonedasB": (10, 3, 1),
        "L1_RuletasA": (13, 3, 1),
        "L1_Barra": (16, 2, 1),
        "L1_Ascensor": (3, 7, 1),
        "L1_Escaleras": (9, 7, 1),

        # Piso 2 (subimos Z = 3)
        "L2_MesasVIP": (1, 1, 5),
        "L2_BarraVIP": (6, 3, 5),
        "L2_BlackjackA": (10, 3, 5),
        "L2_BlackjackB": (14, 4, 5),
        "L2_SalaPoker": (18, 3, 5),
        "L2_Pasillo": (22, 3, 5),
        "L2_Ascensor": (3, 7, 5),
        "L2_Escaleras": (10, 7, 5),

        # Piso 3 (Z = 5)
        "L3_Auditorio": (1, 1, 9),
        "L3_Caja": (6, 3, 9),
        "L3_RestauranteA": (11, 3, 9),
        "L3_RestauranteB": (16, 4, 9),
        "L3_Terraza": (21, 3, 9),
        "L3_Ascensor": (3, 7, 9),
        "L3_Escaleras": (10, 7, 9),

        # Piso 4 (Z = 7)
        "L4_Suites": (1, 1, 13),
        "L4_Pasarela": (7, 3, 13),
        "L4_Penthouse": (13, 3, 13),
        "L4_Ascensor": (3, 7, 13),
        "L4_Escaleras": (10, 7, 13),

        # Nodo intermedio
        "Nodo_Central1": (9, 5, 1)
    }


    for n,(x,y,f) in coords.items():
        g.set_position(n,x,y,f)

    return g
