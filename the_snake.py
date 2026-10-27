from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Все возможные направления движения:
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Повороты: (текущее направление, клавиша) -> новое направление.
# Разворота на противоположное направление в словаре нет.
TURNS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки и её допустимые пределы:
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 5

# Клавиши изменения скорости: клавиша -> изменение скорости.
SPEED_KEYS = {
    pg.K_EQUALS: SPEED_STEP,
    pg.K_PLUS: SPEED_STEP,
    pg.K_KP_PLUS: SPEED_STEP,
    pg.K_MINUS: -SPEED_STEP,
    pg.K_KP_MINUS: -SPEED_STEP,
}

# Шаблон заголовка окна игрового поля:
CAPTION = 'Змейка | Скорость: {speed} | +/- — скорость | Esc — выход'

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов.

    Хранит общие атрибуты: позицию объекта на игровом поле
    и цвет объекта.
    """

    def __init__(self, body_color=None):
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.

        Должен быть переопределён в дочерних классах.
        """
        raise NotImplementedError(
            f'Определите метод draw в классе {type(self).__name__}.'
        )

    def draw_cell(self, position):
        """Рисует одну клетку цветом объекта с рамкой."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко, появляющееся в случайной клетке игрового поля."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Задаёт яблоку случайную позицию на сетке игрового поля.

        Позиция выбирается вне клеток из occupied_positions,
        чтобы яблоко не появилось на теле змейки.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка — список координат сегментов, первый элемент — голова.

    Атрибут position хранит координаты головы змейки.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.speed = SPEED
        self.reset(RIGHT)

    def reset(self, direction=None):
        """Возвращает змейку в начальное состояние в центре поля.

        Если направление не передано, оно выбирается случайно.
        """
        self.position = SCREEN_CENTER
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice(DIRECTIONS)
        self.last = None

    def update_direction(self, direction):
        """Устанавливает новое направление движения змейки."""
        self.direction = direction

    def change_speed(self, step):
        """Изменяет скорость змейки на step в допустимых пределах."""
        self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed + step))

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        При выходе за границу поля змейка появляется
        с противоположной стороны.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        self.position = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, self.position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Затирает хвост змейки и отрисовывает её новую голову.

        Остальные сегменты уже нарисованы на предыдущих кадрах.
        """
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self.draw_cell(self.get_head_position())


def update_caption(speed):
    """Показывает в заголовке окна скорость и подсказки по управлению."""
    pg.display.set_caption(CAPTION.format(speed=speed))


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и закрытие окна.

    Стрелки меняют направление змейки (без разворота назад),
    клавиши +/- меняют скорость. Возвращает False, если нужно
    завершить игру (закрытие окна или Esc), иначе True.
    """
    new_direction = snake.direction
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        if event.type != pg.KEYDOWN:
            continue
        if event.key == pg.K_ESCAPE:
            return False
        if event.key in SPEED_KEYS:
            snake.change_speed(SPEED_KEYS[event.key])
            update_caption(snake.speed)
        new_direction = TURNS.get((snake.direction, event.key), new_direction)
    snake.update_direction(new_direction)
    return True


def main():
    """Создаёт игровые объекты и запускает игровой цикл."""
    # Инициализация PyGame:
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    update_caption(snake.speed)

    while True:
        clock.tick(snake.speed)
        if not handle_keys(snake):
            break
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()
