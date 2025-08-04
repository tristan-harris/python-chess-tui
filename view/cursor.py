class Cursor:
    def __init__(
        self, min_x: int, min_y: int, max_x: int, max_y: int, start_pos: tuple[int, int] = (0, 0)
    ):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

        self.square: tuple[int, int] = start_pos

    def move(self, x_diff: int, y_diff: int):
        new_x: int = self.square[0] + x_diff
        new_y: int = self.square[1] + y_diff
        if self.min_x <= new_x <= self.max_x and self.min_y <= new_y <= self.max_y:
            self.square = (new_x, new_y)
