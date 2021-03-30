class Function:
    def __init__(self, name: str, period: int, deadline: int = 0):
        self.name = name
        if period <= 0:
            print(f"Invalid Period in Function object {self.name}.")
            exit(-1)
        self.period = period
        self.wcet = -1
        self.executed_time = 0
        self.deadline = 0

    def set_wcet(self, value: int):
        if value <= 0:
            print(f"Invalid WCET in Function object {self.name}.")
        self.wcet = value

    def display(self):
        print(f"NAME : {self.name} ; PERIOD : {self.period} ; WCET : {self.wcet}")
