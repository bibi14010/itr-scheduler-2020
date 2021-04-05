class Task:
    def __init__(self, name: str,period: int, resources, deadline: int = 0):
        self.name = name
        self.prio = 0
        if period <= 0:
            print(f"Invalid Period in Function object {self.name}.")
            exit(-1)
        self.period = period
        self.deadline = deadline
        self.resource = resources
        self.wcet = -1
        self.executed_time = 0
        self.times = 0

    def set_wcet(self, value: int):
        if value <= 0:
            print(f"Invalid WCET in Function object {self.name}.")
        self.wcet = value

    def display(self):
        print(f"NAME : {self.name} ; PRIORITY: {self.period} PERIOD : {self.period} ; WCET : {self.wcet}")

    def set_prio(self, new_prio):
        self.prio = new_prio
