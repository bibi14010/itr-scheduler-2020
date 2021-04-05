import sys,os
sys.path.append(os.path.join(os.path.curdir,'src'))
from scheduler import Scheduler
import svgwrite as svg
from typing import List


class Drawer:
    EPAISSEUR = 50

    color = ["forestgreen", "goldenrod", "indianred", "olivedrab", "rosybrown", "teal", "violet"]

    def __init__(self, cases: List[Scheduler.Case], tasks, hyperperiod: int):
        self.cases = cases
        self.tasks = tasks
        self.hyperperiod = hyperperiod

    def draw_schedule(self, name: str):

        draw = svg.Drawing(filename=f"{name}.svg", debug=True)

        # Dessiner les axes horizontaux
        for index in range(len(self.tasks) + 1):
            x_1 = 0
            y_1 = index * self.EPAISSEUR
            x_2 = self.hyperperiod
            y_2 = index * self.EPAISSEUR
            draw.add(draw.line((x_1, y_1), (x_2, y_2), stroke="black"))

        # Dessiner les rectangles représentants l'exécution des tâches
        for case in self.cases:
            if case.name == "None":
                pass
            else:
                x_1 = case.begin_time
                y_1 = case.level * self.EPAISSEUR
                width = case.end_time - case.begin_time
                height = (case.level + self.EPAISSEUR)
                draw.add(draw.rect((x_1, y_1), (width, height), stroke="black", fill=self.color[case.level]))
                draw.add(draw.text(case.name, insert=(x_1, y_1 + (self.EPAISSEUR / 2)), fill="black"))

        # Dessiner les traits rouges représentants les périodes des tâches
        for index in range(len(self.tasks)):
            self.tasks.sort(key=lambda x: x.period)
            tmp_p = 0
            while tmp_p <= self.hyperperiod:
                x_1 = tmp_p
                y_1 = index * self.EPAISSEUR
                x_2 = x_1
                y_2 = y_1 + self.EPAISSEUR
                draw.add(draw.line((x_1, y_1), (x_2, y_2), stroke="red"))
                tmp_p += self.tasks[index].period

        # Écrire le résultat dans un fichier .svg
        draw.save()
