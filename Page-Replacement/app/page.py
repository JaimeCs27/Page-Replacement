class Page:
    def __init__(self, pid, id, direction, isVirtual, isMarked):
        self.pid = pid
        self.id = id
        self.direction = direction
        self.isVirtual = isVirtual
        self.isMarked = isMarked
        
    def __str__(self) -> str:
        return (f"Page(pid={self.pid}, id={self.id}, direction={self.direction}, "
                f"isVirtual={self.isVirtual}, isMarked={self.isMarked})")