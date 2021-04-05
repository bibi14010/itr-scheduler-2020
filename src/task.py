class Task:
    def __init__(self, name: str,period: int, resources, deadline: int = 0):
        self.name = name
        # En cas d'inverion de priorité, la priorité intiale sera en bout de liste
        if period <= 0:
            print(f"Invalid Period in Function object {self.name}.")
            exit(-1)
        self.period = period
        self.prio :list[int]= list()
        self.prio.append(self.period)
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
        self.prio.append(new_prio)

    def get_current_prio(self):
        return self.prio[len(self.prio)-1]