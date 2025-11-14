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
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw_cell(self, surface, position, color, border_color=BORDER_COLOR):
        """Отрисовывает ячейку на указанной поверхности."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, color, rect)
        pg.draw.rect(surface, border_color, rect, 1)

    def draw(self):
        """Метод для отрисовки объекта."""
        raise NotImplementedError(
            "Данный метод должен быть переопределен в дочернем классе"
        )


class Apple(GameObject):
    """Класс для представления яблока в игре."""

    def __init__(self, snake_positions=None):

        if snake_positions is None:
            snake_positions = []
        # Генерируем случайную позицию и передаем ее вместе с цветом в
        # родительский класс
        position = self.randomize_position(snake_positions)
        super().__init__(position, APPLE_COLOR)

    @staticmethod
    def randomize_position(snake_positions):
        """Генерирует случайную позицию на игровом поле."""
        while True:
            new_position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                            randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if new_position not in snake_positions:
                return new_position

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(screen, self.position, self.body_color)


class Snake(GameObject):
    """Класс для представления змейки в игре."""

    def __init__(self):
        # Передаем начальную позицию и цвет в родительский класс
        start_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(start_position, SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]  # Позиция из родительского класса
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
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

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Всегда удаляем последний сегмент (логика роста в main)
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на экране."""
        # Отрисовка всех сегментов кроме головы
        for position in self.positions[:-1]:
            self.draw_cell(screen, position, self.body_color)

        # Отрисовка головы
        self.draw_cell(screen, self.positions[0], self.body_color)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки до начального."""
        self.length = 1
        start_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_position]
        self.position = start_position  # Обновляем позицию
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
            # Словарь для обработки смены направления
            # Ключ - кортеж (текущее_направление, нажатая_клавиша)
            # Значение - новое направление
            direction_map = {
                (UP, pg.K_RIGHT): RIGHT,
                (UP, pg.K_LEFT): LEFT,
                (DOWN, pg.K_RIGHT): RIGHT,
                (DOWN, pg.K_LEFT): LEFT,
                (LEFT, pg.K_UP): UP,
                (LEFT, pg.K_DOWN): DOWN,
                (RIGHT, pg.K_UP): UP,
                (RIGHT, pg.K_DOWN): DOWN
            }

            # Проверяем возможное изменение направления
            new_direction = direction_map.get(
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
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            apple.position = apple.randomize_position(snake.positions)
            # Добавляем сегмент змейке - возвращаем удаленный сегмент
            snake.positions.append(snake.last)
            snake.length += 1

        # Проверка столкновения с собой
        if snake.get_head_position() in snake.positions[1:]:
            # Новая строка - очистка экрана:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple = Apple(snake.positions)  # Создаем новое яблоко при сбросе

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
