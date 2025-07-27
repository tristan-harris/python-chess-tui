class Cursor:
    def __init__(self, color, max_x: int, max_y: int, square: tuple[int, int] = (0, 0)):
        self.color = color
        self.max_x = max_x
        self.max_y = max_y
        self.square: tuple[int, int] = square

    def move(self, x_diff: int, y_diff: int):
        new_x: int = self.square[0] + x_diff
        new_y: int = self.square[1] + y_diff
        if new_x >= 0 and new_x < self.max_x:
            if new_y >= 0 and new_y < self.max_y:
                self.square = (new_x, new_y)
