from typing import Collection


class CycledList:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        self.current_index = 0

    def current(self):
        return self.collection[self.current_index]

    def next(self):
        try:
            ret = self.collection[self.current_index + 1]
        except IndexError:
            self.current_index = 0
            ret = self.collection[self.current_index]
        else:
            self.current_index += 1
        finally:
            return ret

    def previous(self):
        try:
            ret = self.collection[self.current_index - 1]
        except IndexError:
            self.current_index = len(self.collection) - 1
            ret = self.collection[self.current_index]
        else:
            self.current_index -= 1
        finally:
            return ret
