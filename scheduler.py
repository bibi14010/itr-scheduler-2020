from task import Task
from math import pow
from typing import List


class Scheduler:
    class Case:
        # Case object corresponding in a "square" you draw on your paper when scheduling
        def __init__(self, name: str, begin_time: int, end_time: int, level: int):
            self.name = name
            self.begin_time = begin_time
            self.end_time = end_time
            self.level = level

    def __init__(self, tasks: List[Task], hyperperiod: int):
        self.tasks = tasks
        self.hyperperiod = hyperperiod
        # Scheduler virtual clock
        self.time = 0
        self.EDF = list()
        self.RM = list()  # List of Cases

    # Version préemptive
    def schedule_prempt(self, algo: str):
        # Sort the list to have higher priorities first
        list_destination = list()
        tmp_function: Task = None
        if algo == "RM":
            self.__assign_RM_prio()
            tmp_function: Task = self.__get_next_RM_function()
        elif algo == "EDF":
            tmp_function: Task = self.__get_next_EDF_function()
        task_begin_time = 0
        while self.time < self.hyperperiod:
            # Compare t task to t-1 task
            if algo == "RM":
                task = self.__get_next_RM_function()
            elif algo == "EDF":
                task: Task = self.__get_next_EDF_function()
            # Two real tasks case
            if task is not None and tmp_function is not None:
                # Same tasks cases
                if task.name == tmp_function.name:
                    # The task make on step only (Be aware of preemption)
                    tmp_function.executed_time += 1
                else:
                    # Change of tasks (preemption or not). Add the old task
                    list_destination.append(self.Case(tmp_function.name, task_begin_time, self.time - 1,
                                                      self.__get_level(tmp_function.name)))
                    # Update the starting time of the new arrival task
                    task_begin_time = self.time
                    # Then try again with nth new one
                    tmp_function = task
            # Change from nothing executing to something
            if task is not None and tmp_function is None:
                # Add empty case in order to make an empty square in the drawer
                list_destination.append(self.Case("None", task_begin_time, self.time - 1, -1))
                # Update the starting time of the new arrival task
                task_begin_time = self.time
                tmp_function = task
            # Change from something to nothing
            if task is None and tmp_function is not None:
                # Add old task and update the new one to None
                list_destination.append(
                    self.Case(tmp_function.name, task_begin_time, self.time - 1, self.__get_level(tmp_function.name)))
                task_begin_time = self.time
                tmp_function = task
            # Make a step
            self.time += 1
        # Set final version
        if algo == "RM":
            self.RM = list_destination
        elif algo == "EDF":
            self.EDF = list_destination

    # version non préemptive
    def schedule_non_prempt(self, algo):
        list_destination = list()
        if algo == "RM":
            self.__assign_RM_prio()
        while self.time < self.hyperperiod:
            task = None
            if algo == "RM":
                task = self.__get_next_RM_function()
            elif algo == "EDF":
                task = self.__get_next_EDF_function()
            # Get the next task and simply add it. No preemption to take care of.
            if task is not None:
                task.executed_time = task.wcet
                list_destination.append(self.Case(task.name, self.time, self.time + task.wcet,
                                                  self.__get_level(task.name)))
                # Update clock in consequence
                self.time += task.wcet
            else:
                # Nothing to do at this time, make the clock have one step
                self.time += 1
        # Set final list
        if algo == "RM":
            self.RM = list_destination
        elif algo == "EDF":
            self.EDF = list_destination
    # Override the tasks list in order to have it oreder by the size of task'speriod
    # Instead of overriding, maybe we should just swaps
    def __assign_RM_prio(self):
        new_list = list()
        while len(self.tasks) != 0:
            tmp = None
            tmp_function = None
            tmp_index = 0
            index = 0
            for task in self.tasks:
                if tmp is None or task.period < tmp:
                    tmp_index = index
                    tmp = task.period
                    tmp_function = task
                index += 1
            new_list.append(tmp_function)
            self.tasks.pop(tmp_index)
        self.tasks = new_list

    # Fetch the next task
    def __get_next_RM_function(self):
        # New period -> new instance of execution
        for task in self.tasks:
            if self.time >= (task.period * task.times):
                task.executed_time = 0
                task.times += 1
        # From all the tasks, get the first one (remember that the list has been ordered) who still has something to execute
        for task in self.tasks:
            if task.executed_time < task.wcet:
                return task
        return None

    # Get the priority of a task (in order to draw it on the correct line)
    def __get_level(self, name):
        for i in range(len(self.tasks)):
            if self.tasks[i].name == name:
                return i

    # Sufficient condition TODO Necessary condition
    def RM_feasibility(self) -> bool:
        N = (pow(2, 1 / len(self.tasks)) - 1) * len(self.tasks)
        tmp = 0
        for task in self.tasks:
            tmp += task.wcet / task.period
        return tmp <= N

    def __get_next_EDF_function(self):
        for task in self.tasks:
            # New period -> add one time of execution, set executed time to 0 in the new period
            if self.time >= (task.times * task.period):
                task.times += 1
                task.executed_time = 0
        # Initialisation
        tmp_function = None
        tmp_deadline = self.hyperperiod
        for task in self.tasks:
            # The task has something to execute
            if task.executed_time < task.wcet:
                # Memorize the task with the shortest absolute deadline
                if self.__get_next_deadline(task) < tmp_deadline:
                    tmp_deadline = self.__get_next_deadline(task)
                    tmp_function = task
        return tmp_function

    # I think it is sufficiently explicit :3
    def __get_next_deadline(self, task: Task):
        if task is None:
            return -1
        return (task.times * task.period) + task.deadline

    # See the same task definition of RM
    def __get_level(self, name) -> int:
        for i in range(len(self.tasks)):
            if self.tasks[i].name == name:
                return i


    def EDF_feasibility(self) -> bool:
        for task in self.tasks:
            tmp += task.wcet / task.period
        return tmp <= 1
