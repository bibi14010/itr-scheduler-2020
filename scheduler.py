from function import Task
from math import pow
from typing import List

class RateMonotonic:
    class Case:
        # Case object corresponding in a "square" you draw on your paper when scheduling
        def __init__(self, name: str, begin_time: int, end_time: int, level: int):
            self.name = name
            self.begin_time = begin_time
            self.end_time = end_time
            self.level = level

    def __init__(self, functions: List[Task], hyperperiod: int):
        self.functions = functions
        self.hyperperiod = hyperperiod
        # Scheduler virtual clock
        self.time = 0

        self.RM = list()  # List of Cases
    # Version préemptive
    def schedule_prempt(self):
        # Sort the list to have higher priorities first
        self.__assign_RM_prio()
        task_begin_time = 0
        tmp_function: Task = self.__get_next_RM_function()
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

    # version non préemptive
    def schedule_non_prempt(self):
        self.__assign_RM_prio()
        while self.time < self.hyperperiod:
            function = self.__get_next_RM_function()
            # Get the next function and simply add it. No preemption to take care of.
            if function is not None:
                function.executed_time = function.wcet
                function.times += 1
                self.RM.append(self.Case(function.name, self.time, self.time+function.wcet,
                                         self.__get_level(function.name)))
                # Update clock in consequence
                self.time += function.wcet
            else:
                # Nothing to do at this time, make the clock have one step
                self.time += 1

    # Override the functions list in order to have it oreder by the size of function'speriod
    # Instead of overriding, maybe we should just swaps
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

    # Fetch the next function
    def __get_next_RM_function(self):
        # New period -> new instance of execution
        for function in self.functions:
            if self.time >= (function.period * function.times):
                function.executed_time = 0
        # From all the functions, get the first one (remember that the list has been ordered) who still has something to execute
        for function in self.functions:
            if function.executed_time < function.wcet:
                return function
        return None

    # Get the priority of a function (in order to draw it on the correct line)
    def __get_level(self, name):
        for i in range(len(self.functions)):
            if self.functions[i].name == name:
                return i
    # Sufficient condition TODO Necessary condition
    def RM_feasibility(self) -> bool:
        N = (pow(2, 1 / len(self.functions)) - 1) * len(self.functions)
        tmp = 0
        for function in self.functions:
            tmp += function.wcet / function.period
        return tmp <= N


class EarliestDeadlineFirst:
    class Case:
        # Case object corresponding in a "square" you draw on your paper when scheduling
        def __init__(self, name: str, begin_time: int, end_time: int, level: int):
            self.name = name
            self.begin_time = begin_time
            self.end_time = end_time
            self.level = level

    def __init__(self, functions: List[Task], hyperperiod: int):
        self.functions = functions
        self.hyperperiod = hyperperiod
        # Scheduler virtual clock
        self.time = 0

        self.EDF = list()  # List of Cases

    # Version non préemptive
    def schedule_non_prempt(self):
        while self.time < self.hyperperiod:
            # get next function
            function = self.__get_next_EDF_function()
            # if the next function exists, simply add it. No premmption to take care of.
            if function is not None:
                function.executed_time = function.wcet
                self.EDF.append(self.Case(function.name, self.time, self.time + function.executed_time, self.__get_level(function.name)))
                # update the virtual clock
                self.time += function.wcet
            else:
                # None function at t[n], try again on next clock step
                self.time += 1
    # Version préemptive
    def schedule_prempt(self):
        #Initialisation
        task_begin_time = 0
        tmp_function = self.__get_next_EDF_function()
        while self.time < self.hyperperiod:
            # Compare t function to t-1 function
            function = self.__get_next_EDF_function()
            # Two real functions case
            if function is not None and tmp_function is not None:
                # Same functions cases
                if function.name == tmp_function.name :
                    # The function make on step only (Be aware of preemption)
                    tmp_function.executed_time+=1
                else:
                    # Change of functions (preemption or not). Add the old function
                    self.EDF.append(self.Case(tmp_function.name,task_begin_time,self.time-1,self.__get_level(tmp_function.name)))
                    # Update the starting time of the new arrival function
                    task_begin_time=self.time
                    # Then try again with nth new one
                    tmp_function = function
            # Change from nothing executing to something
            if function is not None and tmp_function is None:
                # Add empty case in order to make an empty square in the drawer
                self.EDF.append(self.Case("None",task_begin_time,self.time-1,-1))
                # Update the starting time of the new arrival function
                task_begin_time=self.time
                tmp_function = function
            # Change from something to nothing
            if function is None and tmp_function is not None:
                # Add old function and update the new one to None
                self.EDF.append(self.Case(tmp_function.name,task_begin_time,self.time-1,self.__get_level(tmp_function.name)))
                task_begin_time=self.time
                tmp_function= function
            # Make a step
            self.time += 1


    def __get_next_EDF_function(self):
        for function in self.functions:
            # New period -> add one time of execution, set executed time to 0 in the new period
            if self.time >= (function.times * function.period):
                function.times += 1
                function.executed_time = 0
        # Initialisation
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

    # I think it is sufficiently explicit :3
    def __get_next_deadline(self, function: Task):
        if function is None :
            return -1
        return (function.times * function.period) + function.deadline

    # See the same function definition of RM
    def __get_level(self, name) -> int:
        for i in range(len(self.functions)):
            if self.functions[i].name == name:
                return i

    # TODO
    def EDF_feasibility(self)->bool:
        for function in self.functions:
            tmp += function.wcet / function.period
        return tmp <= 1