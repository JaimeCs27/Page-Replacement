from page import Page

class Symbol:
    def __init__(self, ptr):
        self.ptr = ptr
        self.pages = []

    def addPage(self, id, direction, isVirtual, isMarked):
        page = Page(id, direction, isVirtual, isMarked)
        self.pages.append(page)
    