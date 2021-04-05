from task import Task
from math import pow
from typing import List


class Scheduler:
    class Case:
        # L'objet "Case" représente l'éxécution d'une tâche. Il sera représenté par des Rectangles colorés dans le Drawer
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
        self.output = list()

    # Version préemptive
    def schedule_prempt(self, algo: str):
        if algo == "RM":
            # Trier la liste en fonction de leur période
            self.tasks.sort(key=lambda x: x.period)

        tmp_function: Task = None

        if algo == "RM":
            self.__assign_RM_prio()
            tmp_function: Task = self.__get_next_RM_function()
        elif algo == "EDF":

            tmp_function: Task = self.__get_next_EDF_function()

        task_begin_time = 0


        while self.time < self.hyperperiod:
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
                    self.output.append(self.Case(tmp_function.name, task_begin_time, self.time - 1,
                                                      self.__get_level(tmp_function.name)))
                    # Update the starting time of the new arrival task
                    task_begin_time = self.time
                    # Then try again with nth new one
                    tmp_function = task
            # Change from nothing executing to something
            if task is not None and tmp_function is None:
                # Add empty case in order to make an empty square in the drawer
                self.output.append(self.Case("None", task_begin_time, self.time - 1, -1))
                # Update the starting time of the new arrival task
                task_begin_time = self.time
                tmp_function = task
            # Change from something to nothing
            if task is None and tmp_function is not None:
                # Add old task and update the new one to None
                self.output.append(
                    self.Case(tmp_function.name, task_begin_time, self.time - 1, self.__get_level(tmp_function.name)))
                task_begin_time = self.time
                tmp_function = task
            # Make a step
            self.time += 1

    # version non préemptive
    def schedule_non_prempt(self, algo):
        if algo == "RM":
            # Sort the list by the task's period
            self.tasks.sort(key=lambda x: x.period)

        while self.time < self.hyperperiod:
            task = None
            if algo == "RM":
                task = self.__get_next_RM_function()
            elif algo == "EDF":
                task = self.__get_next_EDF_function()
            # Get the next task and simply add it. No preemption to take care of.
            if task is not None:
                task.executed_time = task.wcet
                self.output.append(self.Case(task.name, self.time, self.time + task.wcet,
                                                  self.__get_level(task.name)))
                # Update clock in consequence
                self.time += task.wcet
            else:
                # Nothing to do at this time, make the clock have one step
                self.time += 1

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

    # Test if the necessary condition for Rate Monotonic is respected
    def rm_necessary_cond(self) -> bool:
        sum = 0
        for task in self.tasks:
            sum += task.wcet / task.period
        return sum<=1
    # Test if the sufficient condition for Rate Monotonic is respected
    def rm_sufficient_cond(self) -> bool:
        N = (pow(2, 1 / len(self.tasks)) - 1) * len(self.tasks)
        sum = 0
        for task in self.tasks:
            sum += task.wcet / task.period
        return sum <= N
    # Test if the necessary condition for Earliest Deadline First is respected
    def edf_necessary_cond(self) -> bool:
        sum = 0
        for task in self.tasks:
            sum += task.wcet / task.period
        return sum <= 1

    # Test if the sufficient condition for Earliest Deadline First is respected
    def edf_sufficient_cond(self) -> bool:
        sum = 0
        for task in self.tasks:
            sum += task.wcet / task.deadline
        return sum <= 1

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
