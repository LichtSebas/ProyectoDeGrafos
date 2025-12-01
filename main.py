# main.py
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QSlider, QMessageBox, QListWidget, QAbstractItemView, QGroupBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from graph import build_large_casino
from views import figure_floor, figure_3d, figure_mold
from viewer_matplotlib_3d import Matplotlib3DWindow

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(Figure(figsize=(6,5)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def draw_figure(self, fig):
        # replace figure in canvas
        self.canvas.figure.clf()
        # draw the incoming figure onto canvas.figure by copying axes
        # simple way: render the provided fig to canvas via canvas.figure = fig
        # but safer: draw fig to canvas using backend renderer
        self.canvas.figure = fig
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Casino Route Simulator (PyQt5)")
        self.setGeometry(100,100,1100,700)
        self.all_paths = []      # Lista de rutas obtenidas
        self.current_path_idx = 0 # Índice de la ruta actualmente mostrada
        
        # people for animation
        self.people = []

        # data & graph
        self.graph = build_large_casino()
        self.current_path = []
        self.animation_index = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(700)  # ms between steps
        self.timer.timeout.connect(self.step_animation)

        # central layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # left: canvas
        self.canvas_widget = CanvasWidget()
        main_layout.addWidget(self.canvas_widget, stretch=3)

        # right: controls
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        right_widget = QWidget()
        scroll_area.setWidget(right_widget)

        right_panel = QVBoxLayout()
        right_widget.setLayout(right_panel)

        main_layout.addWidget(scroll_area, stretch=1)
        # controls
        right_panel.addWidget(QLabel("<b>Controles</b>"))

        # --- Bloque Ruta ---
        grp_route = QGroupBox("Ruta")
        layout_route = QVBoxLayout()
        grp_route.setLayout(layout_route)

        # origin & dest combos
        layout_route.addWidget(QLabel("Origen:"))
        self.cmb_start = QComboBox()
        self.cmb_start.addItems(sorted(self.graph.nodes()))
        self.cmb_start.setCurrentText("L1_Entrada")
        layout_route.addWidget(self.cmb_start)


        layout_route.addWidget(QLabel("Destino:"))
        self.cmb_end = QComboBox()
        self.cmb_end.addItems(sorted(self.graph.nodes()))
        self.cmb_end.setCurrentText("L3_RestauranteA")
        layout_route.addWidget(self.cmb_end)
        
        # Tipo de ruta
        layout_route.addWidget(QLabel("Tipo de ruta:"))
        self.cmb_route_type = QComboBox()
        self.cmb_route_type.addItems([
            "Ruta más rápida",
            "Evitar escaleras",
            "Evitar ascensores"
        ])
        layout_route.addWidget(self.cmb_route_type)

        # Calculate route button
        btn_calc = QPushButton("Calcular Ruta")
        btn_calc.clicked.connect(self.calculate_route)
        layout_route.addWidget(btn_calc)

        # text area for path description
        layout_route.addWidget(QLabel("Descripción de la ruta:"))
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setFixedHeight(160)
        layout_route.addWidget(self.txt_info)
        
        btn_next_route = QPushButton("Ver otra ruta corta")
        btn_next_route.clicked.connect(self.next_route)
        layout_route.addWidget(btn_next_route)

        right_panel.addWidget(grp_route)

        
        # --- Bloque Congestión ---
        grp_congestion = QGroupBox("Congestión")
        layout_congestion = QVBoxLayout()
        grp_congestion.setLayout(layout_congestion)

        # Nodo origen de la arista
        layout_congestion.addWidget(QLabel("Nodo inicio (arista):"))
        self.cmb_edge_start = QComboBox()
        self.cmb_edge_start.addItems(sorted(self.graph.nodes()))
        self.cmb_edge_start.setCurrentText("L1_Entrada")
        layout_congestion.addWidget(self.cmb_edge_start)

        # Nodo fin de la arista
        layout_congestion.addWidget(QLabel("Nodo fin (arista):"))
        self.cmb_edge_end = QComboBox()
        self.cmb_edge_end.addItems(sorted(self.graph.nodes()))
        self.cmb_edge_end.setCurrentText("L1_Ascensor")
        layout_congestion.addWidget(self.cmb_edge_end)

        # Input valor de congestión
        layout_congestion.addWidget(QLabel("Valor de congestión para la arista:"))
        self.spin_edge_congestion = QtWidgets.QSpinBox()
        self.spin_edge_congestion.setMinimum(1)
        self.spin_edge_congestion.setMaximum(100)
        self.spin_edge_congestion.setValue(5)
        layout_congestion.addWidget(self.spin_edge_congestion)

        # Botón aplicar congestión
        btn_apply_edge = QPushButton("Aplicar congestión a la arista")
        btn_apply_edge.clicked.connect(self.apply_edge_congestion)
        layout_congestion.addWidget(btn_apply_edge)

        # Botones random/restore
        btn_rand = QPushButton("Randomizar congestión (aleatorio)")
        btn_rand.clicked.connect(self.randomize_congestion)
        layout_congestion.addWidget(btn_rand)

        btn_restore = QPushButton("Restaurar pesos originales")
        btn_restore.clicked.connect(self.restore_weights)
        layout_congestion.addWidget(btn_restore)

        right_panel.addWidget(grp_congestion)


        # --- Bloque Vistas ---
        grp_views = QGroupBox("Vistas")
        layout_views = QVBoxLayout()
        grp_views.setLayout(layout_views)

        btn_floor1 = QPushButton("Ver Piso 1")
        btn_floor1.clicked.connect(lambda: self.show_floor(1))
        layout_views.addWidget(btn_floor1)

        btn_floor2 = QPushButton("Ver Piso 2")
        btn_floor2.clicked.connect(lambda: self.show_floor(2))
        layout_views.addWidget(btn_floor2)

        btn_floor3 = QPushButton("Ver Piso 3")
        btn_floor3.clicked.connect(lambda: self.show_floor(3))
        layout_views.addWidget(btn_floor3)

        btn_floor4 = QPushButton("Ver Piso 4")
        btn_floor4.clicked.connect(lambda: self.show_floor(4))
        layout_views.addWidget(btn_floor4)

        btn_mold = QPushButton("Ver Molde (solo nodos)")
        btn_mold.clicked.connect(self.show_mold)
        layout_views.addWidget(btn_mold)

        btn_3d = QPushButton("Ver 3D (ruta resaltada)")
        btn_3d.clicked.connect(lambda: self.show_3d(highlight=True))
        layout_views.addWidget(btn_3d)

        btn_3d_interactive = QPushButton("Ver 3D Interactivo")
        btn_3d_interactive.clicked.connect(self.open_3d_interactive)
        layout_views.addWidget(btn_3d_interactive)

        right_panel.addWidget(grp_views)

        btn_heatmap = QPushButton("Mapa de calor de congestión")
        btn_heatmap.clicked.connect(self.show_congestion_heatmap_3d)
        layout_views.addWidget(btn_heatmap)


        # --- Bloque Animación ---
        grp_animation = QGroupBox("Animación")
        layout_animation = QVBoxLayout()
        grp_animation.setLayout(layout_animation)

        btn_start_anim = QPushButton("Iniciar animación paso-a-paso")
        btn_start_anim.clicked.connect(self.start_animation)
        layout_animation.addWidget(btn_start_anim)

        btn_stop_anim = QPushButton("Detener animación")
        btn_stop_anim.clicked.connect(self.stop_animation)
        layout_animation.addWidget(btn_stop_anim)

        right_panel.addWidget(grp_animation)

        # --- Bloque Edición de Grafo ---
        grp_edit = QGroupBox("Edición de Grafo")
        layout_edit = QVBoxLayout()
        grp_edit.setLayout(layout_edit)

        # Agregar nodo
        layout_edit.addWidget(QLabel("Agregar nodo:"))
        self.txt_new_node = QtWidgets.QLineEdit()
        self.txt_new_node.setPlaceholderText("Nombre del nodo")
        layout_edit.addWidget(self.txt_new_node)

        coord_layout = QHBoxLayout()
        self.spin_x = QtWidgets.QDoubleSpinBox(); self.spin_x.setRange(-1000,1000); self.spin_x.setValue(0)
        self.spin_y = QtWidgets.QDoubleSpinBox(); self.spin_y.setRange(-1000,1000); self.spin_y.setValue(0)
        self.spin_z = QtWidgets.QDoubleSpinBox(); self.spin_z.setRange(-1000,1000); self.spin_z.setValue(0)
        coord_layout.addWidget(QLabel("X:")); coord_layout.addWidget(self.spin_x)
        coord_layout.addWidget(QLabel("Y:")); coord_layout.addWidget(self.spin_y)
        coord_layout.addWidget(QLabel("Z:")); coord_layout.addWidget(self.spin_z)
        layout_edit.addLayout(coord_layout)

        btn_add_node = QPushButton("Agregar nodo")
        btn_add_node.clicked.connect(self.add_node)
        layout_edit.addWidget(btn_add_node)

        # Agregar arista
        layout_edit.addWidget(QLabel("Agregar arista:"))
        self.cmb_edge_a = QComboBox(); self.cmb_edge_a.addItems(sorted(self.graph.nodes()))
        self.cmb_edge_b = QComboBox(); self.cmb_edge_b.addItems(sorted(self.graph.nodes()))
        layout_edit.addWidget(QLabel("Nodo inicio:")); layout_edit.addWidget(self.cmb_edge_a)
        layout_edit.addWidget(QLabel("Nodo fin:")); layout_edit.addWidget(self.cmb_edge_b)

        self.spin_edge_weight = QtWidgets.QDoubleSpinBox(); self.spin_edge_weight.setRange(0,1000); self.spin_edge_weight.setValue(1)
        layout_edit.addWidget(QLabel("Peso:")); layout_edit.addWidget(self.spin_edge_weight)

        self.cmb_edge_type = QComboBox(); self.cmb_edge_type.addItems(["normal", "escalera", "ascensor"])
        layout_edit.addWidget(QLabel("Tipo de arista:")); layout_edit.addWidget(self.cmb_edge_type)

        btn_add_edge = QPushButton("Agregar arista")
        btn_add_edge.clicked.connect(self.add_edge)
        layout_edit.addWidget(btn_add_edge)

        # Eliminar nodo
        layout_edit.addWidget(QLabel("Eliminar nodo:"))
        self.cmb_del_node = QComboBox(); self.cmb_del_node.addItems(sorted(self.graph.nodes()))
        layout_edit.addWidget(self.cmb_del_node)
        btn_del_node = QPushButton("Eliminar nodo")
        btn_del_node.clicked.connect(self.delete_node)
        layout_edit.addWidget(btn_del_node)

        # Eliminar arista
        layout_edit.addWidget(QLabel("Eliminar arista:"))
        self.cmb_del_edge_a = QComboBox(); self.cmb_del_edge_a.addItems(sorted(self.graph.nodes()))
        self.cmb_del_edge_b = QComboBox(); self.cmb_del_edge_b.addItems(sorted(self.graph.nodes()))
        layout_edit.addWidget(QLabel("Nodo inicio:")); layout_edit.addWidget(self.cmb_del_edge_a)
        layout_edit.addWidget(QLabel("Nodo fin:")); layout_edit.addWidget(self.cmb_del_edge_b)
        btn_del_edge = QPushButton("Eliminar arista")
        btn_del_edge.clicked.connect(self.delete_edge)
        layout_edit.addWidget(btn_del_edge)

        # Guardar/Cargar grafo
        btn_save = QPushButton("Guardar escenario")
        btn_save.clicked.connect(self.save_scenario)
        layout_edit.addWidget(btn_save)

        btn_load = QPushButton("Cargar escenario")
        btn_load.clicked.connect(self.load_scenario)
        layout_edit.addWidget(btn_load)


        right_panel.addWidget(grp_edit)

        # initial draw
        self.show_floor(1)

    def slider_changed(self):
        v = self.slider.value() / 100.0
        self.graph.set_dynamic_multiplier(v)
        self.lbl_mult.setText(f"Multiplicador actual: {v:.2f}x")
        # if there's a path calculated, update displayed cost & text
        if self.current_path:
            dist, path = self.graph.dijkstra(self.cmb_start.currentText(), self.cmb_end.currentText())
            self.txt_info.setPlainText(self.format_route_text(dist, path))
    def open_3d_interactive(self):
        fig = figure_3d(self.graph)
        self.win3d = Matplotlib3DWindow(fig)
        self.win3d.show()
    def apply_zone_congestion(self):
        selected_items = self.list_zones.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Zonas", "Selecciona al menos un nodo para aplicar congestión.")
            return

        extra = self.spin_zone.value() / 1.0  # convertir a float si quieres decimales

        for item in selected_items:
            node = item.text()
            self.graph.set_zone_congestion(node, extra)  # <--- importante, usa el método del graph

        self.txt_info.append(f"Congestión de {extra:.2f} aplicada en: {', '.join([i.text() for i in selected_items])}")
        self.show_3d(highlight=True)

    def apply_edge_congestion(self):
        start = self.cmb_edge_start.currentText()
        end = self.cmb_edge_end.currentText()
        value = self.spin_edge_congestion.value() / 1.0  # float

        if start not in self.graph.adj or end not in self.graph.adj:
            QMessageBox.warning(self, "Error", "Nodos inválidos.")
            return

        # aplicar congestión solo a esa arista
        self.graph.set_zone_congestion((start, end), value)

        self.txt_info.append(f"Congestión de {value:.2f} aplicada a la arista {start} -> {end}")
        self.show_3d(highlight=True)


    def randomize_congestion(self):
        self.graph.randomize_congestion()
        self.txt_info.append("Congestión aleatoria aplicada.")
        # redraw active view with weights visible if it's 3D or floor: just refresh 3D
        self.show_3d(highlight=True)

    def restore_weights(self):
        self.graph.restore_original()
        self.txt_info.append("Pesos restaurados a sus valores originales.")
        self.show_floor(1)

    def format_route_text(self, dist, path):
        s = f"Ruta: {' -> '.join(path)}\n"
        s += f"Distancia total (coste): {dist:.2f}\n\n"
        # detalle tramo a tramo
        s += "Tramos:\n"
        for i in range(len(path)-1):
            a,b = path[i], path[i+1]
            # find weight from a to b
            w = next((edge[1] for edge in self.graph.adj[a] if edge[0]==b), None)
            s += f"  {a} -> {b} (coste: {w:.2f})\n"
        return s

    def show_floor(self, floor):
        fig = figure_floor(self.graph, floor, highlight_path=self.current_path, show_edges=True, show_weights=True)
        self.canvas_widget.draw_figure(fig)

    def show_mold(self):
        fig = figure_floor(self.graph, floor=1, highlight_path=None, show_edges=False)
        # draw all floors' nodes in single 'mold' style: use figure_mold if wanted
        from views import figure_mold
        fig = figure_mold(self.graph)
        self.canvas_widget.draw_figure(fig)

    def show_3d(self, highlight=False):
        fig = figure_3d(self.graph, highlight_path=self.current_path if highlight else None, show_weights=False)
        self.canvas_widget.draw_figure(fig)

    def show_congestion_heatmap_3d(self):
        """
        Mapa de calor 3D de congestión: aristas coloreadas según peso.
        """
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        from matplotlib.cm import ScalarMappable
        from mpl_toolkits.mplot3d.art3d import Line3DCollection

        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111, projection='3d')

        # recolectar todas las aristas y sus pesos
        segments = []
        weights = []

        for a in self.graph.adj:
            x1, y1, z1 = self.graph.positions_3d[a]
            for b, w, t in self.graph.adj[a]:
                # evitar duplicar aristas
                if a < b:
                    x2, y2, z2 = self.graph.positions_3d[b]
                    segments.append([[x1, y1, z1], [x2, y2, z2]])
                    weights.append(w)

        # normalizar colores
        cmap = plt.cm.Reds
        norm = mcolors.Normalize(vmin=min(weights), vmax=max(weights))
        colors = [cmap(norm(w)) for w in weights]

        # crear colección de líneas
        lc = Line3DCollection(segments, colors=colors, linewidths=2)
        ax.add_collection(lc)

        # dibujar nodos
        for n, (x, y, z) in self.graph.positions_3d.items():
            ax.scatter(x, y, z, s=80, c='blue')
            ax.text(x, y, z, n, fontsize=8)

        # colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label("Peso actual / congestión")

        # ajustar vista
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.view_init(elev=30, azim=45)

        self.canvas_widget.draw_figure(fig)


    # Animation logic
    def start_animation(self):
        if not self.current_path or len(self.current_path) < 2:
            QMessageBox.information(self, "Animación", "Calcula una ruta primero (Calcular Ruta).")
            return
        self.animation_index = 0
        self.timer.start()
        self.txt_info.append("\nAnimación iniciada...")

    def stop_animation(self):
        self.timer.stop()
        self.txt_info.append("Animación detenida.")

    def step_animation(self):
        # show partial path up to animation_index
        if self.animation_index >= len(self.current_path)-1:
            self.timer.stop()
            self.txt_info.append("Animación completada.")
            return
        partial = self.current_path[:self.animation_index+2]  # up to next node
        # Draw 3D with partial path highlighted
        fig = figure_3d(self.graph, highlight_path=partial, show_weights=False)
        self.canvas_widget.draw_figure(fig)
        # update info area with current step
        a = self.current_path[self.animation_index]
        b = self.current_path[self.animation_index+1]
        w = next((edge[1] for edge in self.graph.adj[a] if edge[0]==b), 0)
        self.txt_info.append(f"Paso {self.animation_index+1}: {a} -> {b} (coste: {w:.2f})")
        self.animation_index += 1
    def calculate_route(self):
        start = self.cmb_start.currentText()
        end = self.cmb_end.currentText()
        
        # obtener tipo de ruta seleccionado
        route_type = self.cmb_route_type.currentText()
        avoid_types = []
        if route_type == "Evitar escaleras":
            avoid_types = ["stairs"]
        elif route_type == "Evitar ascensores":
            avoid_types = ["elevator"]

        
        # obtener 3 rutas más cortas usando penalización
        self.all_paths = self.graph.k_shortest_paths(
            start, end, k=3, avoid_types=avoid_types
        )
        self.current_path_idx = 0
        
        if not self.all_paths:
            QMessageBox.warning(self, "Ruta", "No existe ruta entre los nodos seleccionados.")
            self.txt_info.setPlainText("No hay ruta.")
            return

        # mostrar la primera ruta por defecto
        self.show_current_route()


    def show_current_route(self):
        path = self.all_paths[self.current_path_idx]
        self.current_path = path  # para animación y 3D

        # construir texto
        text = f"Ruta {self.current_path_idx+1} (coste: {sum(next(edge[1] for edge in self.graph.adj[path[j]] if edge[0]==path[j+1]) for j in range(len(path)-1)):.2f}): {' -> '.join(path)}\n"
        text += "  Tramos:\n"
        for j in range(len(path)-1):
            a,b = path[j], path[j+1]
            w = next(edge[1] for edge in self.graph.adj[a] if edge[0] == b)
            text += f"    {a} -> {b} (coste: {w:.2f})\n"

        self.txt_info.setPlainText(text)
        self.show_3d(highlight=True)
    def next_route(self):
        if not self.all_paths:
            QMessageBox.information(self, "Rutas", "Calcula una ruta primero.")
            return
        # siguiente ruta
        self.current_path_idx = (self.current_path_idx + 1) % len(self.all_paths)
        self.show_current_route()

    # Prueba de nodos :( espero que funcione por el bien de mi nota
    def add_node(self):
        name = self.txt_new_node.text().strip()
        x, y, z = self.spin_x.value(), self.spin_y.value(), self.spin_z.value()
        if not name:
            QMessageBox.warning(self, "Error", "Ingresa un nombre válido para el nodo.")
            return
        if name in self.graph.adj:
            QMessageBox.warning(self, "Error", "El nodo ya existe.")
            return
        self.graph.add_node(name, pos=(x, y, z))
        QMessageBox.information(self, "Nodo agregado", f"Nodo '{name}' agregado correctamente.")
        # actualizar combos
        for cmb in [self.cmb_edge_a, self.cmb_edge_b, self.cmb_del_node, self.cmb_del_edge_a, self.cmb_del_edge_b]:
            cmb.addItem(name)
        self.show_3d()

    def add_edge(self):
        a = self.cmb_edge_a.currentText()
        b = self.cmb_edge_b.currentText()
        w = self.spin_edge_weight.value()
        t = self.cmb_edge_type.currentText()
        if a == b:
            QMessageBox.warning(self, "Error", "No se puede crear una arista al mismo nodo.")
            return
        self.graph.add_edge(a, b, w, t)
        QMessageBox.information(self, "Arista agregada", f"Arista {a} -> {b} agregada correctamente.")
        self.show_3d()

    def delete_node(self):
        n = self.cmb_del_node.currentText()
        if n not in self.graph.adj:
            QMessageBox.warning(self, "Error", "Nodo no existe.")
            return
        self.graph.remove_node(n)
        QMessageBox.information(self, "Nodo eliminado", f"Nodo '{n}' eliminado correctamente.")
        # actualizar combos
        for cmb in [self.cmb_edge_a, self.cmb_edge_b, self.cmb_del_node, self.cmb_del_edge_a, self.cmb_del_edge_b]:
            cmb.clear(); cmb.addItems(sorted(self.graph.nodes()))
        self.show_3d()

    def delete_edge(self):
        a, b = self.cmb_del_edge_a.currentText(), self.cmb_del_edge_b.currentText()
        if a not in self.graph.adj or b not in [edge[0] for edge in self.graph.adj[a]]:
            QMessageBox.warning(self, "Error", "Arista no existe.")
            return
        self.graph.remove_edge(a, b)
        QMessageBox.information(self, "Arista eliminada", f"Arista {a} -> {b} eliminada correctamente.")
        self.show_3d()
    
    # Guardar/Cargar grafo
    def save_scenario(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar escenario", "", "JSON Files (*.json)")
        if filename:
            self.graph.save_scenario(filename)
            QMessageBox.information(self, "Guardar", f"Escenario guardado en {filename}")

    def load_scenario(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar escenario", "", "JSON Files (*.json)")
        if filename:
            self.graph.load_scenario(filename)
            # actualizar combos
            nodes = sorted(self.graph.nodes())
            for cmb in [self.cmb_edge_a, self.cmb_edge_b, self.cmb_del_node, self.cmb_del_edge_a, self.cmb_del_edge_b]:
                cmb.clear()
                cmb.addItems(nodes)
            self.show_3d()
            QMessageBox.information(self, "Cargar", f"Escenario cargado desde {filename}")
    # people animation
    def generate_people(self, num_people=5):
        import random
        self.people = []
        for _ in range(num_people):
            # elige una ruta al azar entre las calculadas
            if not self.all_paths:
                continue
            path = random.choice(self.all_paths)
            color = (random.random(), random.random(), random.random())  # RGB random
            self.people.append({"path": path, "index": 0, "color": color})
        self.txt_info.append(f"{len(self.people)} personas generadas para animación.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
