class LineSegment:
    def __init__(self, left: float, right: float):
        if right < left:
            raise ValueError("The beginning of a line segment cannot exceed its end.")

        self.left = left
        self.right = right

    @property
    def length(self):
        return self.right - self.left

    @property
    def center(self):
        return (self.right + self.left) / 2

    def __str__(self):
        return f"[{self.left}, {self.right}]"

    def __repr__(self):
        return str(self)

    def copy(self):
        return LineSegment(self.left, self.right)
