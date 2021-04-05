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

    def __init__(self, tasks: List[Task], hyperperiod: int, resources=None):
        self.tasks = tasks
        self.levels = [(task.name, task.period) for task in self.tasks]
        self.levels.sort(key=lambda x: x[1])

        self.hyperperiod = hyperperiod
        # Scheduler virtual clock
        self.time = 0
        self.resources = resources
        self.output = list()

    # Version préemptive
    def schedule_prempt(self, algo: str):
        # Assigner la priorité aux tâches
        if algo == "RM":
            self.__assign_RM_prio()
            tmp_function: Task = self.__get_next_RM_function()
        elif algo == "EDF":
            self.__assign_EDF_prio()
            tmp_function: Task = self.__get_next_EDF_function()

        task_begin_time = 0
        tmp_function: Task = None

        while self.time < self.hyperperiod:
            if algo == "RM":
                task = self.__get_next_RM_function()
            elif algo == "EDF":
                self.__assign_EDF_prio()
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
                    # Libérer les ressources de la tâche
                    all(resource.release_resource() for resource in tmp_function.resource)
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
                # Libérer les ressources de la tâche
                all(resource.release_resource() for resource in tmp_function.resource)
                task_begin_time = self.time
                tmp_function = task
            # Make a step
            self.time += 1

    # version non préemptive
    def schedule_non_prempt(self, algo):
        if algo == "RM":
            # Sort the list by the task's period
            self.tasks.sort(key=lambda x: x.period)
            self.__assign_RM_prio()

        while self.time < self.hyperperiod:
            task = None
            if algo == "RM":
                task = self.__get_next_RM_function()
            elif algo == "EDF":
                self.__assign_EDF_prio()
                task = self.__get_next_EDF_function()
            # Get the next task and simply add it. No preemption to take care of.
            if task is not None:
                task.executed_time = task.wcet
                self.output.append(self.Case(task.name, self.time, self.time + task.wcet,
                                             self.__get_level(task.name)))
                # Relacher les ressources prises par la tâche
                all(resource.release_resource() for resource in task.resource)
                # Incrémenter l'horloge du temps d'exécution
                self.time += task.wcet
            else:
                # Nothing to do at this time, make the clock have one step
                self.time += 1

    # Fetch the next task
    def __get_next_RM_function(self):
        # Réinitialiser le temps d'éxécution et incrémenter le nombre d'éxécution lors d'une nouvelle période
        for task in self.tasks:
            if self.time >= (task.period * task.times):
                task.executed_time = 0
                task.times += 1
        # La liste étant ordonnée par priorité, pendre la première qui à quelquechose à exécuter, si elle n'est pas bloquée
        waiting_tasks = [x for x in self.tasks if x.executed_time < x.wcet]

        waiting_tasks.sort(key=lambda x: x.get_current_prio())
        for task in waiting_tasks:
            if all(resource.get_resource(task) for resource in task.resource):
                print( all(resource.get_resource(task) for resource in task.resource))
                print(f"Chosing {task.name} ")
                return task
        return None

    def __assign_RM_prio(self):
        # Trier la liste en fonction de leur période (plus petite période en premier)
        self.tasks.sort(key=lambda x: x.period)
        tmp_prio = 0
        # Mettre la priorité des tâches : Plus la valeur est petite, plus priotité est importante
        for task in self.tasks:
            tmp_prio += 1
            task.prio.append(tmp_prio)

    def __assign_EDF_prio(self):
        # Trier la liste en fonction de la deadline absolu la plus courte
        self.tasks.sort(key=lambda t: self.__get_next_deadline(t))
        # Mettre la priorité des tâches : Plus la valeur est petite, plus priotité est importante
        tmp_prio = 0
        for task in self.tasks:
            tmp_prio += 1
            task.prio[len(task.prio) - 1] = tmp_prio

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
            # Vérifier que la tâche à quelquechose à éxécuter et qu'elle n'est pas bloqué par ses ressources
            if task.executed_time < task.wcet and all(resource.get_resource(task) for resource in task.resource):
                # Memorize the task with the shortest absolute deadline
                if self.__get_next_deadline(task) < tmp_deadline:
                    tmp_deadline = self.__get_next_deadline(task)
                    tmp_function = task
        return tmp_function

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
        return sum <= 1

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

    def __get_next_deadline(self, task: Task):
        if task is None:
            return -1
        return (task.times * task.period) + task.deadline

    def __get_level(self, name) -> int:
        for index in range(len(self.levels)):
            if self.levels[index][0] == name:
                return index
