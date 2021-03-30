from function import Function
from math import pow
from typing import List

class RateMonotonic:
    class Case:

        def __init__(self, name: str, begin_time: int, end_time: int, level: int):
            self.name = name
            self.begin_time = begin_time
            self.end_time = end_time
            self.level = level

    def __init__(self, functions: List[Function], hyperperiod: int):
        self.functions = functions
        self.hyperperiod = hyperperiod
        self.time = 0

        self.RM = list()  # List of Cases
    # Version préemptive TODO version non-préemptive
    def schedule(self):
        # Sort the list to have higher priorities first
        self.__assign_RM_prio()
        task_begin_time = 0
        tmp_function: Function = self.__get_next_RM_function()
        while self.time < self.hyperperiod:
            function = self.__get_next_RM_function()
            if function is not None and tmp_function is not None:
                # New function appears
                if function.name != tmp_function.name:
                    self.RM.append(self.Case(tmp_function.name, task_begin_time, self.time - 1,
                                             self.__get_level(tmp_function.name)))
                    task_begin_time = self.time
            elif function is not None and tmp_function is None:
                self.RM.append(self.Case("None", task_begin_time, self.time - 1, -1))
                task_begin_time = self.time
            elif function is None and tmp_function is not None:
                tmp_function.executed_time = tmp_function.wcet
                self.RM.append(self.Case(tmp_function.name, task_begin_time, self.time - 1,
                                         self.__get_level(tmp_function.name)))
                task_begin_time = self.time
            if tmp_function is not None:
                tmp_function.executed_time += 1
            tmp_function = function
            self.time += 1

    def __assign_RM_prio(self):
        new_list = list()
        while len(self.functions) != 0:
            tmp = None
            tmp_function = None
            tmp_index = 0
            index = 0
            for function in self.functions:
                if tmp is None or function.period < tmp:
                    tmp_index = index
                    tmp = function.period
                    tmp_function = function
                index += 1
            new_list.append(tmp_function)
            self.functions.pop(tmp_index)
        self.functions = new_list

    def __get_next_RM_function(self):
        for function in self.functions:
            if self.time % function.period == 0:
                function.executed_time = 0
        for function in self.functions:
            if function.executed_time < function.wcet:
                return function
        return None

    def __get_level(self, name):
        for i in range(len(self.functions)):
            if self.functions[i].name == name:
                return i

    def RM_feasibility(self) -> bool:
        N = (pow(2, 1 / len(self.functions)) - 1) * len(self.functions)
        tmp = 0
        for function in self.functions:
            tmp += function.wcet / function.period
        return tmp <= N


class EarliestDeadlineFirst:
    class Case:

        def __init__(self, name: str, begin_time: int, end_time: int, level: int):
            self.name = name
            self.begin_time = begin_time
            self.end_time = end_time
            self.level = level

    def __init__(self, functions: List[Function], hyperperiod: int):
        self.functions = functions
        self.hyperperiod = hyperperiod
        self.time = 0

        self.EDF = list()  # List of Cases

    # Version non préemptive TODO version prémptive
    def schedule(self):
        while self.time < self.hyperperiod:
            function = self.__get_next_EDF_function()
            if function is not None:
                function.executed_time = function.wcet
                function.times += 1
                self.EDF.append(self.Case(function.name, self.time, self.time + function.executed_time, self.__get_level(function.name)))
                self.time += function.wcet
            else:
                self.time += 1

    def __get_next_EDF_function(self):
        for function in self.functions:
            # New period
            if self.time >= (function.times * function.period):
                function.executed_time = 0

        tmp_function = None
        tmp_deadline = self.hyperperiod
        for function in self.functions:
            # The function has something to execute
            if function.executed_time < function.wcet:
                # Memorize the function with the shortest absolute deadline
                if self.__get_next_deadline(function) < tmp_deadline:
                    tmp_deadline = self.__get_next_deadline(function)
                    tmp_function = function
        return tmp_function

    def __get_next_deadline(self, function: Function):
        return (function.times * function.period) + function.deadline

    def __get_level(self, name) -> int:
        for i in range(len(self.functions)):
            if self.functions[i].name == name:
                return i

    def EDF_feasibility(self)->bool:
        for function in self.functions:
            tmp += function.wcet / function.period
        return tmp <= 1