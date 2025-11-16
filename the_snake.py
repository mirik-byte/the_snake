"""Импортируем модуль для игры и для определения случайных элементов."""

from random import choice, randint

import pygame as pg

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

# Сопоставление направлений и клавиш
DIRECTION_MAP = {
    (UP, pg.K_RIGHT): RIGHT,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN
}

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
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        # Если позиция не указана, размещаем по центру
        self.position = position if position else (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color = body_color

    def draw_cell(self, surface, position):
        """Отрисовывает ячейку на указанной поверхности."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, self.body_color, rect)
        pg.draw.rect(surface, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод для отрисовки объекта."""
        raise NotImplementedError(
            'Данный метод должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Класс для представления яблока в игре."""

    def __init__(self, snake_positions=None):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(snake_positions or [])

    def randomize_position(self, snake_positions):
        """Генерирует случайную позицию на игровом поле и устанавливает её."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in snake_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(screen, self.position)


class Snake(GameObject):
    """Класс для представления змейки в игре."""

    def __init__(self):
        # Явно инициализируем все атрибуты перед вызовом reset()
        self.positions = []
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку и обрабатывает столкновения."""
        head_x, head_y = self.get_head_position()

        direction_x, direction_y = self.direction
        head_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        head_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (head_x, head_y)

        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на экране."""
        for position in self.positions[:-1]:
            self.draw_cell(screen, position)

        self.draw_cell(screen, self.positions[0])

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки до начального."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((RIGHT, LEFT, DOWN, UP))
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            new_direction = DIRECTION_MAP.get(
                (game_object.direction, event.key)
            )
            if new_direction:
                game_object.next_direction = new_direction


def main():
    """Основная функция игры, содержащая главный цикл."""
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.positions.append(snake.last)
            snake.length += 1

        # Проверка столкновения с собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
