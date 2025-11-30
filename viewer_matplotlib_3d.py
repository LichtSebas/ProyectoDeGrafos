from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class Matplotlib3DWindow(QWidget):
    def __init__(self, fig):
        super().__init__()
        self.setWindowTitle("Visor 3D interactivo (Matplotlib)")

        self.canvas = FigureCanvasQTAgg(fig)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.canvas.draw()
