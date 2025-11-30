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
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, stretch=1)

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

    def calculate_route(self):
        start = self.cmb_start.currentText()
        end = self.cmb_end.currentText()
        dist, path = self.graph.dijkstra(start, end)
        if dist == float('inf') or not path:
            QMessageBox.warning(self, "Ruta", "No existe ruta entre los nodos seleccionados.")
            self.txt_info.setPlainText("No hay ruta.")
            return
        self.current_path = path
        self.txt_info.setPlainText(self.format_route_text(dist, path))
        # show 3D view with highlighted route by default
        self.show_3d(highlight=True)

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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
