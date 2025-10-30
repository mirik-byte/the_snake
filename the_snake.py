"""Импортируем модуль для игры и для определения случайных элементов."""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Метод для отрисовки объекта."""
        pass


class Apple(GameObject):
    """Класс для представления яблока в игре."""

    def __init__(self, snake_positions=None):
        super().__init__()
        if snake_positions is None:
            snake_positions = []
        self.position = self.randomize_position(snake_positions)
        self.body_color = APPLE_COLOR

    @staticmethod
    def randomize_position(snake_positions):
        """Генерирует случайную позицию на игровом поле."""
        while True:
            horizontal = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            vertical = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (horizontal, vertical)
            if new_position not in snake_positions:
                return new_position

    def draw(self):
        """Отрисовывает яблоко на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс для представления змейки в игре."""

    def __init__(self):
        super().__init__()
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple):
        """Перемещает змейку и обрабатывает столкновения."""
        head_x, head_y = self.get_head_position()

        # Вычисляем новую позицию головы
        # Так как направления движения представляют из себя кортежи, то мы их
        # можем использовать для упрощённого вычисления координат змеи
        # С помощью оператора % происходит перемещение змеи через рамки экрана
        direction_x, direction_y = self.direction
        head_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        head_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (head_x, head_y)

        # Проверяем столкновение с собой
        if new_head in self.positions:
            self.reset()
            return

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Проверяем съедание яблока
        if new_head == apple.position:
            apple.position = apple.randomize_position(self.positions)
            self.length += 1
        else:
            if len(self.positions) > 1:
                self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на экране."""
        # Отрисовка всех сегментов кроме головы
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки до начального."""
        # Затираем все сегменты
        for position in self.positions:
            last_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice((RIGHT, LEFT, DOWN, UP))
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры, содержащая главный цикл."""
    pygame.init()

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move(apple)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
