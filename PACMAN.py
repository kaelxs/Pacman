import pygame
import sys
import math
import random
from typing import List, Tuple, Optional

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
FPS = 60

# Colores
NEGRO = (15, 15, 25)
AZUL_OSCURO = (25, 30, 50)
AZUL_NEON = (0, 191, 255)
AMARILLO_NEON = (255, 223, 0)
ROSA_NEON = (255, 20, 147)
VERDE_NEON = (57, 255, 20)
ROJO_NEON = (255, 69, 0)
MORADO_NEON = (186, 85, 211)
BLANCO = (255, 255, 255)
DORADO = (255, 215, 0)

# Tamaño de celdas
CELDA = 25

class PacManGame:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("🎮 Pac-Man con Algoritmo Minimax")
        self.reloj = pygame.time.Clock()
        
        # Mapa del juego (1=pared, 0=punto, 2=espacio vacío)
        self.mapa = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,0,1],
            [1,0,0,0,0,1,0,0,0,1,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,1,0,1,1,1,2,1,1,2,1,1,1,0,1,1,1,1],
            [1,1,1,1,0,1,2,2,2,2,2,2,2,2,1,0,1,1,1,1],
            [1,1,1,1,0,1,2,1,1,2,2,1,1,2,1,0,1,1,1,1],
            [2,2,2,2,0,2,2,1,2,2,2,2,1,2,2,0,2,2,2,2],
            [1,1,1,1,0,1,2,1,1,1,1,1,1,2,1,0,1,1,1,1],
            [1,1,1,1,0,1,2,2,2,2,2,2,2,2,1,0,1,1,1,1],
            [1,1,1,1,0,1,1,1,2,1,1,2,1,1,1,0,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
            [1,1,0,1,0,1,0,1,1,1,1,1,1,0,1,0,1,0,1,1],
            [1,0,0,0,0,1,0,0,0,1,1,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        # Posiciones iniciales
        self.pacman_pos = [10, 15]
        self.fantasmas = [
            {'pos': [9, 9], 'color': ROSA_NEON, 'nombre': 'Blinky', 'ultimas_pos': []}
        ]
        
        # Estado del juego
        self.puntos_totales = sum(fila.count(0) for fila in self.mapa)
        self.puntos_comidos = 0
        self.puntuacion = 0
        self.juego_terminado = False
        self.victoria = False
        self.tiempo_animacion = 0
        self.particulas = []
        
    def es_posicion_valida(self, pos):
        x, y = pos
        if 0 <= y < len(self.mapa) and 0 <= x < len(self.mapa[0]):
            return self.mapa[y][x] != 1
        return False
    
    def obtener_movimientos_validos(self, pos, evitar_repeticion=True, ultimas_pos=[]):
        x, y = pos
        movimientos = []
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # arriba, abajo, izquierda, derecha
        
        for dx, dy in direcciones:
            nueva_pos = [x + dx, y + dy]
            if self.es_posicion_valida(nueva_pos):
                if evitar_repeticion and nueva_pos in ultimas_pos[-2:]:
                    continue
                movimientos.append(nueva_pos)
        return movimientos or self.obtener_movimientos_validos(pos, False, [])
    
    def distancia_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def es_estado_terminal(self, pacman_pos, fantasmas_pos):
        """Determina si el estado actual es terminal (victoria o derrota)"""
        # Colisión con algún fantasma
        for fantasma_pos in fantasmas_pos:
            if pacman_pos == fantasma_pos:
                return True
        
        # Todos los puntos recolectados
        if self.mapa[pacman_pos[1]][pacman_pos[0]] == 0:
            puntos_restantes = sum(fila.count(0) for fila in self.mapa)
            if puntos_restantes == 0:
                return True
        
        return False
    
    def evaluar_estado(self, pacman_pos, fantasmas_pos):
        """
        Función de evaluación para Minimax:
        - Valores altos son buenos para Pacman (MAX)
        - Valores bajos son buenos para los fantasmas (MIN)
        """
        # Estado terminal: colisión con fantasma
        for fantasma_pos in fantasmas_pos:
            if pacman_pos == fantasma_pos:
                return -float('inf')
        
        # Estado terminal: todos los puntos recolectados
        if self.mapa[pacman_pos[1]][pacman_pos[0]] == 0:
            puntos_restantes = sum(fila.count(0) for fila in self.mapa)
            if puntos_restantes == 0:
                return float('inf')
        
        # Calcular distancias a los fantasmas
        distancias = [self.distancia_manhattan(pacman_pos, f) for f in fantasmas_pos]
        distancia_minima = min(distancias) if distancias else 10
        
        # Calcular puntos cercanos
        puntos_cercanos = 0
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = pacman_pos[0] + dx, pacman_pos[1] + dy
            if 0 <= ny < len(self.mapa) and 0 <= nx < len(self.mapa[0]):
                if self.mapa[ny][nx] == 0:
                    puntos_cercanos += 10
        
        # Puntos en la posición actual
        punto_actual = 20 if self.mapa[pacman_pos[1]][pacman_pos[0]] == 0 else 0
        
        # Evaluación compuesta
        return (distancia_minima * 10 +  # Prioridad: mantener distancia de fantasmas
                puntos_cercanos +        # Segundo: recolectar puntos cercanos
                punto_actual)            # Tercero: puntos en posición actual
    
    def minimax(self, pacman_pos, fantasmas_pos, profundidad, es_maximizando):
        """
        Implementación del algoritmo Minimax:
        - pacman_pos: posición actual de Pacman (jugador MAX)
        - fantasmas_pos: lista de posiciones de fantasmas (jugador MIN)
        - profundidad: profundidad restante del árbol de búsqueda
        - es_maximizando: True si es el turno de MAX (Pacman), False para MIN (fantasmas)
        """
        # Condición de parada por profundidad o estado terminal
        if profundidad == 0 or self.es_estado_terminal(pacman_pos, fantasmas_pos):
            return self.evaluar_estado(pacman_pos, fantasmas_pos), None

        if es_maximizando:
            # Turno de Pacman (MAX)
            mejor_valor = float('-inf')
            mejor_movimiento = None
            
            movimientos = self.obtener_movimientos_validos(pacman_pos)
            if not movimientos:
                return self.evaluar_estado(pacman_pos, fantasmas_pos), None
            
            for movimiento in movimientos:
                # Simular movimiento de Pacman
                valor, _ = self.minimax(movimiento, fantasmas_pos, 
                                      profundidad - 1, False)
                
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            
            return mejor_valor, mejor_movimiento
        else:
            # Turno de Fantasmas (MIN)
            peor_valor = float('inf')
            peor_movimiento = None
            
            # Solo tenemos un fantasma ahora
            movimientos_fantasma = self.obtener_movimientos_validos(fantasmas_pos[0])
            
            for movimiento in movimientos_fantasma:
                # Simular movimiento del fantasma
                valor, _ = self.minimax(pacman_pos, [movimiento], 
                                      profundidad - 1, True)
                
                if valor < peor_valor:
                    peor_valor = valor
                    peor_movimiento = movimiento
            
            return peor_valor, peor_movimiento
    
    def mover_pacman_con_minimax(self):
        """Mueve Pacman usando el algoritmo Minimax"""
        fantasmas_pos = [f['pos'] for f in self.fantasmas]
        _, mejor_movimiento = self.minimax(self.pacman_pos, fantasmas_pos, 3, True)
        
        if mejor_movimiento:
            self.pacman_pos = mejor_movimiento
            # Comer punto si hay uno
            if self.mapa[mejor_movimiento[1]][mejor_movimiento[0]] == 0:
                self.mapa[mejor_movimiento[1]][mejor_movimiento[0]] = 2
                self.puntos_comidos += 1
                self.puntuacion += 10
                self.crear_particula(mejor_movimiento, DORADO)
                
                if self.puntos_comidos >= self.puntos_totales:
                    self.victoria = True
                    self.juego_terminado = True
    
    def mover_fantasmas(self):
        """Mueve los fantasmas con comportamiento semi-aleatorio"""
        for fantasma in self.fantasmas:
            # Registrar posición actual
            fantasma['ultimas_pos'].append(fantasma['pos'][:])
            if len(fantasma['ultimas_pos']) > 5:
                fantasma['ultimas_pos'].pop(0)
            
            movimientos = self.obtener_movimientos_validos(
                fantasma['pos'], 
                True, 
                fantasma['ultimas_pos']
            )
            
            if movimientos:
                # Comportamiento para perseguir a Pacman
                distancias = [self.distancia_manhattan(mov, self.pacman_pos) 
                             for mov in movimientos]
                fantasma['pos'] = movimientos[distancias.index(min(distancias))]
    
    def crear_particula(self, pos, color):
        self.particulas.append({
            'pos': [pos[0] * CELDA + CELDA//2, pos[1] * CELDA + CELDA//2],
            'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
            'color': color,
            'vida': 30
        })
    
    def actualizar_particulas(self):
        for particula in self.particulas[:]:
            particula['pos'][0] += particula['vel'][0]
            particula['pos'][1] += particula['vel'][1]
            particula['vida'] -= 1
            
            if particula['vida'] <= 0:
                self.particulas.remove(particula)
    
    def verificar_colisiones(self):
        for fantasma in self.fantasmas:
            if self.pacman_pos == fantasma['pos']:
                self.juego_terminado = True
                self.victoria = False
                return
    
    def dibujar_mapa(self):
        for y, fila in enumerate(self.mapa):
            for x, celda in enumerate(fila):
                rect = pygame.Rect(x * CELDA, y * CELDA, CELDA, CELDA)
                
                if celda == 1:  # Pared
                    pygame.draw.rect(self.pantalla, AZUL_OSCURO, rect)
                    pygame.draw.rect(self.pantalla, AZUL_NEON, rect, 1)
                elif celda == 0:  # Punto
                    centro = (x * CELDA + CELDA//2, y * CELDA + CELDA//2)
                    brillo = int(50 + 30 * math.sin(self.tiempo_animacion * 0.2))
                    pygame.draw.circle(self.pantalla, (255, 223, brillo), centro, 3)
    
    def dibujar_pacman(self):
        centro = (self.pacman_pos[0] * CELDA + CELDA//2, 
                 self.pacman_pos[1] * CELDA + CELDA//2)
        
        # Dibujar Pacman con boca animada
        angulo_boca = int(30 * math.sin(self.tiempo_animacion * 0.4))
        pygame.draw.circle(self.pantalla, AMARILLO_NEON, centro, CELDA//2 - 2)
        
        # Etiqueta MAX
        font = pygame.font.Font(None, 16)
        texto = font.render("MAX", True, BLANCO)
        self.pantalla.blit(texto, (centro[0] - 15, centro[1] - 25))
    
    def dibujar_fantasmas(self):
        for fantasma in self.fantasmas:
            centro = (fantasma['pos'][0] * CELDA + CELDA//2, 
                     fantasma['pos'][1] * CELDA + CELDA//2)
            
            # Dibujar fantasma
            pygame.draw.circle(self.pantalla, fantasma['color'], 
                              (centro[0], centro[1] - 5), CELDA//2 - 2)
            
            # Etiqueta MIN
            font = pygame.font.Font(None, 16)
            texto = font.render("MIN", True, BLANCO)
            self.pantalla.blit(texto, (centro[0] - 15, centro[1] - 30))
            
            # Ojos
            pygame.draw.circle(self.pantalla, BLANCO, (centro[0] - 6, centro[1] - 4), 4)
            pygame.draw.circle(self.pantalla, BLANCO, (centro[0] + 6, centro[1] - 4), 4)
            pygame.draw.circle(self.pantalla, NEGRO, (centro[0] - 6, centro[1] - 4), 2)
            pygame.draw.circle(self.pantalla, NEGRO, (centro[0] + 6, centro[1] - 4), 2)
    
    def dibujar_particulas(self):
        for particula in self.particulas:
            alpha = max(0, particula['vida'] * 8)
            if alpha > 0:
                pos = (int(particula['pos'][0]), int(particula['pos'][1]))
                pygame.draw.circle(self.pantalla, particula['color'], pos, 2)
    
    def dibujar_interfaz(self):
        font_titulo = pygame.font.Font(None, 36)
        font_info = pygame.font.Font(None, 24)
        
        # Título del algoritmo
        texto_algoritmo = font_titulo.render("ALGORITMO MINIMAX", True, AZUL_NEON)
        self.pantalla.blit(texto_algoritmo, (10, 10))
        
        # Información de jugadores
        texto_info = font_info.render("Pacman = MAX | Fantasmas = MIN", True, BLANCO)
        self.pantalla.blit(texto_info, (10, 45))
        
        # Puntuación
        texto_puntos = font_titulo.render(f"SCORE: {self.puntuacion}", True, AMARILLO_NEON)
        self.pantalla.blit(texto_puntos, (10, 550))
        
        # Progreso
        texto_progreso = font_info.render(f"Puntos: {self.puntos_comidos}/{self.puntos_totales}", 
                                         True, VERDE_NEON)
        self.pantalla.blit(texto_progreso, (250, 555))
        
        # Estado del juego
        if self.juego_terminado:
            if self.victoria:
                texto_estado = font_titulo.render("¡VICTORIA! - Presiona R para reiniciar", 
                                                True, VERDE_NEON)
            else:
                texto_estado = font_titulo.render("GAME OVER - Presiona R para reiniciar", 
                                                True, ROJO_NEON)
            
            rect_texto = texto_estado.get_rect(center=(ANCHO//2, 100))
            self.pantalla.blit(texto_estado, rect_texto)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    self.__init__()  # Reiniciar juego
        
        return True
    
    def actualizar(self):
        if not self.juego_terminado:
            # Mover Pacman con Minimax cada 15 frames
            if self.tiempo_animacion % 15 == 0:
                self.mover_pacman_con_minimax()
            
            # Mover fantasmas cada 20 frames
            if self.tiempo_animacion % 20 == 0:
                self.mover_fantasmas()
            
            self.verificar_colisiones()
        
        self.actualizar_particulas()
        self.tiempo_animacion += 1
    
    def dibujar(self):
        self.pantalla.fill(NEGRO)
        
        # Estrellas de fondo
        for i in range(50):
            x = (i * 37) % ANCHO
            y = (i * 73) % 500
            brillo = int(100 + 50 * math.sin(self.tiempo_animacion * 0.05 + i))
            pygame.draw.circle(self.pantalla, (brillo, brillo, brillo), (x, y), 1)
        
        self.dibujar_mapa()
        self.dibujar_particulas()
        self.dibujar_pacman()
        self.dibujar_fantasmas()
        self.dibujar_interfaz()
        
        pygame.display.flip()
    
    def ejecutar(self):
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Ejecutar el juego
if __name__ == "__main__":
    juego = PacManGame()
    juego.ejecutar()