=============================================
🎰 Casino Route Simulator (PyQt5)
=============================================

Simulador interactivo de rutas dentro de un casino multi-piso, con visualización 2D/3D, animación del camino y gestión de congestión.

=============================================
🚀 Características
=============================================

🧭 Cálculo de rutas

- Ruta más rápida usando Dijkstra.

- Evitar escaleras.

- Evitar ascensores.

- Cálculo de k rutas más cortas (k=3).

- Visualización detallada tramo a tramo.

🔥 Congestión dinámica

- Aplicación de congestión por arista o zonas (nodos).

- Congestión aleatoria.

- Restauración de pesos originales.

- Mapa de calor 3D que muestra congestión por color.

🎨 Vistas interactivas

- Vista de pisos 1, 2, 3 y 4.

- Vista de molde (solo nodos).

- Vista 3D con ruta resaltada.

- Vista 3D completamente interactiva con rotación.

- Animación paso a paso del recorrido.

- Animación simultánea de “personas” siguiendo rutas (soporte incluido).

🧱 Editor de grafo completo

- Agregar nodos (con coordenadas X, Y, Z).

- Eliminar nodos.

- Agregar aristas con peso y tipo:

    - normal

    - escalera

    - ascensor

- Eliminar aristas.

- Guardar escenario en JSON.

- Cargar escenarios desde JSON.

=============================================
🛠 Tecnologías
=============================================
✎ Python 3.10+

✎ PyQt5
 – Interfaz gráfica (GUI)

✎ Matplotlib
 – Visualización 2D/3D

✎ NetworkX
 – Algoritmos de grafos

✎ JSON
 – Guardado de escenarios

=============================================
⚡ Instalación rápida
=============================================
- git clone https://github.com/tuusuario/casino-route-simulator.git
- cd casino-route-simulator

# Crear entorno virtual
- python -m venv venv

# Activar entorno
- source venv/bin/activate     # Linux/macOS
- venv\Scripts\activate        # Windows

# Instalar dependencias
- pip install -r requirements.txt

# Ejecutar el simulador
- python main.py

=============================================
🎨 Uso
=============================================

1. Selecciona origen y destino en el panel derecho.

2. Selecciona el tipo de ruta (rápida, evitando escaleras, evitando ascensores).

3. Presiona Calcular Ruta.

4. Explora vistas 2D/3D o animación paso a paso.

4. Modifica nodos, aristas y congestión.

5. Guarda o carga escenarios en JSON.

6. Visualiza la congestión en un mapa de calor 3D.

=============================================
📂 Estructura
=============================================
casino-route-simulator/
│
├── main.py                     
├── graph.py                    
├── views.py                    
├── viewer_matplotlib_3d.py     
│
├── scenarios/                  # Escenarios JSON (opcional)
├── requirements.txt
└── README.md

=============================================
💡 Próximas mejoras sugeridas
=============================================

- Soporte para guardar animaciones como GIF/MP4.

- Exportación de rutas a PDF.

- Modo nocturno (dark mode).

- Algoritmo A* con heurística por pisos.

=============================================
📌 Licencia
=============================================

MIT License

Copyright (c) 2025 
Licht (Sebastián Gonzales Aroni)
