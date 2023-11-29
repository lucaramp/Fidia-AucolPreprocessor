class ListQueue:
    def __init__(self):
        self.__list_as_queue = list()

    def put(self, item):
        self.__list_as_queue.insert(0, item)

    def get(self):
        if len(self.__list_as_queue) < 1:
            return None
        return self.__list_as_queue.pop(0)

    def peek(self):
        if len(self.__list_as_queue) < 1:
            return None
        return self.__list_as_queue[0]
    def size(self):
        return len(self.__list_as_queue)