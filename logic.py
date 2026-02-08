import math
import random
from typing import List, Tuple, Optional


class Ball:
    """Класс, представляющий шарик в игре."""
    
    def __init__(self, x: float, y: float, radius: float = 15, 
                 color: Tuple[int, int, int] = None, 
                 velocity: Tuple[float, float] = None):
        """
        Инициализация шарика.
        
        Args:
            x, y: Позиция центра шарика
            radius: Радиус шарика
            color: RGB цвет (r, g, b) в диапазоне 0-255
            velocity: Скорость (vx, vy)
        """
        self.x = x
        self.y = y
        self.radius = radius
        
        # Если цвет не указан, генерируем случайный яркий цвет
        if color is None:
            # Генерируем яркий цвет (избегаем слишком темных)
            self.color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
        else:
            self.color = color
        
        # Если скорость не указана, генерируем случайную
        if velocity is None:
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 2 * math.pi)
            self.vx = speed * math.cos(angle)
            self.vy = speed * math.sin(angle)
        else:
            self.vx, self.vy = velocity
    
    def update(self, dt: float, screen_width: float, screen_height: float):
        """
        Обновляет позицию шарика с учетом скорости и границ экрана.
        
        Args:
            dt: Время, прошедшее с последнего обновления (в секундах)
            screen_width: Ширина экрана
            screen_height: Высота экрана
        """
        # Обновляем позицию
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Отскок от границ экрана
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx = -abs(self.vx)
        
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.vy = -abs(self.vy)
    
    def get_distance(self, other: 'Ball') -> float:
        """Вычисляет расстояние между центрами двух шариков."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_colliding(self, other: 'Ball') -> bool:
        """Проверяет, сталкиваются ли два шарика."""
        distance = self.get_distance(other)
        return distance < (self.radius + other.radius)
    
    def mix_color(self, other: 'Ball') -> Tuple[int, int, int]:
        """
        Смешивает цвета двух шариков.
        Использует нелинейное смешивание для получения интересных результатов.
        Белый цвет (255, 255, 255) считается плохим результатом.
        """
        r1, g1, b1 = self.color
        r2, g2, b2 = other.color
        
        # Используем среднее геометрическое для более интересного смешивания
        # Это дает более насыщенные и интересные цвета
        new_r = int(math.sqrt((r1 * r1 + r2 * r2) / 2))
        new_g = int(math.sqrt((g1 * g1 + g2 * g2) / 2))
        new_b = int(math.sqrt((b1 * b1 + b2 * b2) / 2))
        
        # Немного добавляем случайности для разнообразия
        variation = 10
        new_r = max(0, min(255, new_r + random.randint(-variation, variation)))
        new_g = max(0, min(255, new_g + random.randint(-variation, variation)))
        new_b = max(0, min(255, new_b + random.randint(-variation, variation)))
        
        # Проверяем, не получился ли слишком белый цвет
        # Если все компоненты близки к 255, делаем цвет более насыщенным
        if new_r > 240 and new_g > 240 and new_b > 240:
            # Смещаем в сторону более насыщенного цвета
            avg = (new_r + new_g + new_b) // 3
            new_r = min(255, avg + random.randint(0, 50))
            new_g = min(255, avg + random.randint(0, 50))
            new_b = min(255, avg + random.randint(0, 50))
        
        return (new_r, new_g, new_b)


class GameLogic:
    """Основной класс, управляющий игровой логикой."""
    
    def __init__(self, screen_width: float = 800, screen_height: float = 600, 
                 delete_zone_height: float = 50):
        """
        Инициализация игровой логики.
        
        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
            delete_zone_height: Высота зоны удаления внизу экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.delete_zone_height = delete_zone_height
        
        # Список шариков на экране
        self.balls: List[Ball] = []
        
        # Инвентарь (шарики, которые "всосали")
        self.inventory: List[Ball] = []
        
        # Позиция мыши для "всасывания"
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        
        # Радиус "всасывания" (на каком расстоянии шарики могут быть втянуты)
        self.suction_radius = 100.0
        
        # Флаг, что мышь зажата (для всасывания)
        self.mouse_pressed = False
    
    def add_ball(self, x: float = None, y: float = None, 
                 radius: float = None, color: Tuple[int, int, int] = None):
        """
        Добавляет новый шарик на экран.
        
        Args:
            x, y: Позиция (если None, то случайная)
            radius: Радиус (если None, то случайный 10-20)
            color: Цвет (если None, то случайный)
        """
        if x is None:
            x = random.uniform(50, self.screen_width - 50)
        if y is None:
            y = random.uniform(50, self.screen_height - 50)
        if radius is None:
            radius = random.uniform(10, 20)
        
        ball = Ball(x, y, radius, color)
        self.balls.append(ball)
    
    def update(self, dt: float):
        """
        Обновляет состояние игры.
        
        Args:
            dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Обновляем позиции всех шариков
        for ball in self.balls:
            ball.update(dt, self.screen_width, self.screen_height)
        
        # Обрабатываем столкновения и смешивание цветов
        self._handle_collisions()
        
        # Обрабатываем "всасывание" шариков мышкой
        if self.mouse_pressed:
            self._handle_suction()
        
        # Проверяем шарики в зоне удаления
        self._check_delete_zone()
    
    def _handle_collisions(self):
        """Обрабатывает столкновения шариков и смешивание их цветов."""
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                if ball1.is_colliding(ball2):
                    # Смешиваем цвета
                    new_color = ball1.mix_color(ball2)
                    # Применяем новый цвет к обоим шарикам
                    ball1.color = new_color
                    ball2.color = new_color
                    # Шарики не отталкиваются, просто проходят друг через друга
    
    def _handle_suction(self):
        """Обрабатывает 'всасывание' шариков мышкой."""
        balls_to_remove = []
        
        for ball in self.balls:
            # Вычисляем расстояние от мыши до центра шарика
            dx = self.mouse_x - ball.x
            dy = self.mouse_y - ball.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Если шарик в радиусе всасывания, перемещаем его в инвентарь
            if distance < self.suction_radius:
                # Увеличиваем скорость приближения к мыши
                pull_strength = (self.suction_radius - distance) / self.suction_radius
                ball.vx += dx * pull_strength * 0.5
                ball.vy += dy * pull_strength * 0.5
                
                # Если шарик очень близко к мыши, "всасываем" его
                if distance < ball.radius * 2:
                    balls_to_remove.append(ball)
                    # Создаем копию шарика для инвентаря
                    inventory_ball = Ball(ball.x, ball.y, ball.radius, ball.color, (0, 0))
                    self.inventory.append(inventory_ball)
        
        # Удаляем "всосанные" шарики с экрана
        for ball in balls_to_remove:
            if ball in self.balls:
                self.balls.remove(ball)
    
    def _check_delete_zone(self):
        """Проверяет шарики в зоне удаления и удаляет их."""
        delete_zone_y = self.screen_height - self.delete_zone_height
        
        balls_to_delete = []
        for ball in self.balls:
            # Если шарик попал в зону удаления (нижняя часть экрана)
            if ball.y + ball.radius >= delete_zone_y:
                balls_to_delete.append(ball)
        
        for ball in balls_to_delete:
            if ball in self.balls:
                self.balls.remove(ball)
    
    def set_mouse_position(self, x: float, y: float):
        """Устанавливает позицию мыши."""
        self.mouse_x = x
        self.mouse_y = y
    
    def set_mouse_pressed(self, pressed: bool):
        """Устанавливает состояние кнопки мыши (зажата/отпущена)."""
        self.mouse_pressed = pressed
    
    def release_ball_from_inventory(self, x: float, y: float):
        """
        'Выплвывает' шарик из инвентаря обратно на экран.
        
        Args:
            x, y: Позиция, где появится шарик
        """
        if self.inventory:
            # Берем последний шарик из инвентаря
            ball = self.inventory.pop()
            # Устанавливаем новую позицию
            ball.x = x
            ball.y = y
            # Даем случайную скорость
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 2 * math.pi)
            ball.vx = speed * math.cos(angle)
            ball.vy = speed * math.sin(angle)
            # Добавляем обратно на экран
            self.balls.append(ball)
    
    def get_balls(self) -> List[Ball]:
        """Возвращает список всех шариков на экране."""
        return self.balls
    
    def get_inventory(self) -> List[Ball]:
        """Возвращает список шариков в инвентаре."""
        return self.inventory
    
    def get_delete_zone_bounds(self) -> Tuple[float, float, float, float]:
        """
        Возвращает границы зоны удаления.
        
        Returns:
            (x, y, width, height) зоны удаления
        """
        return (0, self.screen_height - self.delete_zone_height, 
                self.screen_width, self.delete_zone_height)
    
    def clear_all_balls(self):
        """Удаляет все шарики с экрана."""
        self.balls.clear()
    
    def clear_inventory(self):
        """Очищает инвентарь."""
        self.inventory.clear()
