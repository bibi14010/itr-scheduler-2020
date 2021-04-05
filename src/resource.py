from task import Task


class Resource:
    def __init__(self, name:str):
        self.name = name
        self.working_task : Task= None

    def get_resource(self, task: Task) -> bool:
        if self.working_task is None or self.working_task.name == task.name:
            # La ressource libre devient occupée par la nouvelle tâche
            self.working_task = task
            return True
        else:
            # La nouvelle tâche est bloquée, la tache utilisant la ressource hérite de la priorité
            self.working_task.prio.append(task.get_current_prio())
            print(f"working task is {self.working_task.name}. {task.name} is blocked")
            return False

    def release_resource(self):
        # La tâche libère la ressource et récupère son ancienne priorité si elle en a récupéré une
        if len(self.working_task.prio)>1:
            self.working_task.prio.pop()
        self.working_task = None





