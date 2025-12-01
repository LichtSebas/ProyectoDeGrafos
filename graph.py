# graph.py
import heapq
import random
import networkx as nx
import json

class Graph:
    def __init__(self):
        # adjacency: node -> list of [neighbor, weight, type]
        self.adj = {}
        self.positions_3d = {}  # node -> (x,y,floor)
        self.original_weights = {}  # (a,b) -> w
        self.dynamic_multiplier = 1.0
        self.congestion_zones = {}

    def k_shortest_paths(self, start, end, k=3, avoid_types=None):
        """
        Devuelve las k rutas más cortas desde start hasta end.
        avoid_types: lista de tipos de aristas a evitar, e.g., ['stairs']
        """
        if start not in self.adj or end not in self.adj:
            return []

        # heap de rutas: (costo, [camino])
        heap = [(0, [start])]
        results = []

        while heap and len(results) < k:
            cost, path = heapq.heappop(heap)
            node = path[-1]

            if node == end:
                results.append(path)
                continue

            for neighbor, w, t in self.adj.get(node, []):
                if neighbor in path:
                    continue  # evitar ciclos
                if avoid_types and t in avoid_types:
                    continue
                heapq.heappush(heap, (cost + w, path + [neighbor]))

        return results

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
    # Prebua de nodos y aristas
    # ----------------------------------------------------------------------
    
    def add_node(self, name, pos=(0,0,0)):
        if name in self.adj:
            return False  # nodo ya existe
        self.adj[name] = []
        self.positions_3d[name] = pos
        return True

    def remove_node(self, name):
        if name not in self.adj:
            return False
        # eliminar todas las aristas que apuntan a este nodo
        for neighbor, edges in self.adj.items():
            self.adj[neighbor] = [e for e in edges if e[0] != name]
        # eliminar nodo y posición
        del self.adj[name]
        if name in self.positions_3d:
            del self.positions_3d[name]
        # eliminar pesos originales asociados
        keys_to_delete = [k for k in self.original_weights if name in k]
        for k in keys_to_delete:
            del self.original_weights[k]
        return True

    def remove_edge(self, a, b):
        if a in self.adj:
            self.adj[a] = [e for e in self.adj[a] if e[0] != b]
        if b in self.adj:
            self.adj[b] = [e for e in self.adj[b] if e[0] != a]
        self.original_weights.pop((a,b), None)
        self.original_weights.pop((b,a), None)

    # ==========================================================
    # GUARDAR Y CARGAR ESCENARIOS EN JSON
    # ==========================================================
    def save_scenario(self, filename):
        data = {
            "positions": self.positions_3d,  # {nodo: [x,y,z]}
            "edges": [],  # lista de aristas
        }

        for a in self.adj:
            for b, w, t in self.adj[a]:
                # para evitar duplicados: solo guarda a < b
                if a < b:
                    data["edges"].append({
                        "start": a,
                        "end": b,
                        "weight": w,
                        "type": t
                    })
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Escenario guardado en {filename}")


    def load_scenario(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        
        # limpiar grafo actual
        self.adj = {}
        self.positions_3d = {}
        self.original_weights = {}

        # restaurar posiciones
        self.positions_3d = {k: tuple(v) for k,v in data.get("positions", {}).items()}

        # restaurar aristas
        for edge in data.get("edges", []):
            a, b = edge["start"], edge["end"]
            w, t = edge["weight"], edge["type"]
            self.add_edge(a, b, w, t)
        
        print(f"Escenario cargado desde {filename}")
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

    def dijkstra_with_penalty(self, start, end, avoid_types=None):
        """
        avoid_types: lista de tipos de aristas a penalizar, ej: ["escalera"]
        """
        import heapq

        avoid_types = avoid_types or []

        # copia de pesos con penalización
        dist = {node: float('inf') for node in self.nodes()}
        prev = {node: None for node in self.nodes()}
        dist[start] = 0
        heap = [(0, start)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w, t in self.adj[u]:  # suponiendo tu adj lista: (vecino, peso, tipo)
                # si es tipo a evitar, agregamos penalización
                w_penalized = w + (50 if t in avoid_types else 0)  # ejemplo: 50 extra
                if dist[u] + w_penalized < dist[v]:
                    dist[v] = dist[u] + w_penalized
                    prev[v] = u
                    heapq.heappush(heap, (dist[v], v))

        # reconstruir path
        path = []
        node = end
        while node:
            path.insert(0, node)
            node = prev[node]
        if path[0] != start:
            return float('inf'), []  # no hay ruta
        return dist[end], path



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
