=============================================
🎰 Casino Route Simulator (PyQt5)
=============================================

Simulador interactivo de rutas dentro de un casino multi-piso, con visualización 2D/3D, animación del camino y gestión de congestión.

=============================================
🚀 Características
=============================================

➤ Rutas óptimas: calcula rutas más rápidas, evita escaleras o ascensores.

➤ Congestión dinámica: aplica valores manuales o aleatorios a aristas y nodos.

➤ Vistas interactivas: pisos 1-4, molde de nodos, 3D resaltando rutas, mapa de calor de congestión.

➤ Edición de grafo: agregar/eliminar nodos y aristas, guardar/cargar escenarios en JSON.

=============================================
🛠 Tecnologías
=============================================
✎ Python 3.10+

✎ PyQt5
 – GUI

✎ Matplotlib
 – Visualización 2D/3D

✎ NetworkX
 – Grafos

=============================================
⚡ Instalación rápida
=============================================
git clone https://github.com/tuusuario/casino-route-simulator.git
cd casino-route-simulator
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py

=============================================
🎨 Uso
=============================================

1. Selecciona origen y destino.

2. Elige tipo de ruta y presiona Calcular Ruta.

3. Explora vistas 2D/3D o animación paso a paso.

4. Modifica nodos, aristas y congestión.

5. Guarda o carga escenarios en JSON.

=============================================
📂 Estructura
=============================================
main.py
graph.py
views.py
viewer_matplotlib_3d.py
scenarios/    (no aplicado porque es opcional)
requirements.txt
README.md

=============================================
📌 Licencia
=============================================

MIT License

Copyright (c) 2025 Licht (Sebastián Gonzales Aroni)
