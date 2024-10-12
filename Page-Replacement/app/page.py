class Page:
    def __init__(self, pid, id, direction, isVirtual, isMarked, pointer):
        self.pid = pid
        self.id = id
        self.direction = direction
        self.isVirtual = isVirtual
        self.isMarked = isMarked
        self.pointer = pointer
        self.fragmentation = 0
        
    def __str__(self) -> str:
        return (f"Page(pid={self.pid}, id={self.id}, direction={self.direction}, "
                f"isVirtual={self.isVirtual}, isMarked={self.isMarked}, pointer={self.pointer})")