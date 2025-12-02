from abc import ABC,abstractmethod

class Parser(ABC):

    @abstractmethod
    def parse():
        pass



class JsonParser(Parser):

    def parse():
        ...
