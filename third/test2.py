from abc import ABC, abstractmethod

class SupportHandler(ABC):
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler):
        self._next_handler = handler
        return handler
    
    def handle(self, problem: str, level: int):

        if self.can_handle(level):
            self.resolve(problem)
        elif self._next_handler:
            print(f"  → Передаю дальше...")
            self._next_handler.handle(problem, level)
        else:
            print(f"Никто не смог решить проблему: {problem}")
    
    @abstractmethod
    def can_handle(self, level: int) -> bool:
        pass
    
    @abstractmethod
    def resolve(self, problem: str):
        pass



class JuniorSupport(SupportHandler):
    
    def can_handle(self, level: int) -> bool:
        return level <= 1  
    
    def resolve(self, problem: str):
        print(f"Младший специалист решил: '{problem}'")


class SeniorSupport(SupportHandler):
    
    def can_handle(self, level: int) -> bool:
        return level <= 2 
    
    def resolve(self, problem: str):
        print(f"Старший специалист решил: '{problem}'")


class ManagerSupport(SupportHandler):
    
    def can_handle(self, level: int) -> bool:
        return level <= 3 
    
    def resolve(self, problem: str):
        print(f"Менеджер решил: '{problem}'")


if __name__ == "__main__":
    junior = JuniorSupport()
    senior = SeniorSupport()
    manager = ManagerSupport()
    
    junior.set_next(senior).set_next(manager)

    print("(уровень 1)")
    junior.handle("Не включается компьютер", 1)
    
    print("Звонок: 'Пропал интернет' (уровень 2)")
    junior.handle("Пропал интернет", 2)

    print("Звонок: 'Сервер упал' (уровень 3)")
    junior.handle("Сервер упал", 3)
    
    print("Звонок: 'Ядерный реактор взорвался' (уровень 4)")
    junior.handle("Ядерный реактор взорвался", 4)