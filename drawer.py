import svgwrite as svg
from scheduler import RateMonotonic


class Drawer:
    ECHELLE = 50

    color = ["forestgreen","goldenrod","indianred","olivedrab","rosybrown","teal","violet"]

    def __init__(self, cases: list[RateMonotonic.Case], periods: list[int], hyperperiod: int):
        self.cases = cases
        self.periods = periods
        self.hyperperiod = hyperperiod

    def draw_schedule(self, name:str):

        draw = svg.Drawing(filename=f"{name}.svg", debug=True)

        # Draw lines for better convenience
        for index in range(len(self.periods)+1):
            x_1 = 0
            y_1 = index * self.ECHELLE
            x_2 = self.hyperperiod
            y_2 = index * self.ECHELLE
            draw.add(draw.line((x_1, y_1), (x_2, y_2), stroke="black"))

        # Draw rectangles for visible schedule
        for case in self.cases:
            print(f"Case {case.name} arriving on {case.begin_time} anf finishing on {case.end_time} with order of {case.level}")
            if case.name == "None":
                pass
            else:
                x_1 = case.begin_time
                y_1 = case.level * self.ECHELLE
                width = case.end_time - case.begin_time
                height = (case.level + self.ECHELLE)
                draw.add(draw.rect((x_1, y_1), (width, height), stroke="black", fill=self.color[case.level]))
                draw.add(draw.text(case.name, insert=(x_1, y_1 + (self.ECHELLE / 2)), fill="black"))

        #Draw periods for convencience
        for index in range(len(self.periods)):
            tmp_p =0
            while tmp_p <= self.hyperperiod :
                x_1 = tmp_p
                y_1 = index * self.ECHELLE
                x_2 = x_1
                y_2 = y_1 + self.ECHELLE
                draw.add(draw.line((x_1, y_1), (x_2, y_2), stroke="red"))
                tmp_p += self.periods[index]

        # Save the drawing into the file (svg syntax)
        draw.save()