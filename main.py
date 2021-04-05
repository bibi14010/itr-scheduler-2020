import json
import xml.etree.ElementTree as ET
from math import ceil,gcd
from src.task import Task
from src.drawer import Drawer
from src.scheduler import Scheduler
from typing import List


SCALE=10
def ppcm(list):
    lcm = list[0]
    for i in list[1:]:
        lcm = lcm * i // gcd(lcm, i)
    return lcm

def get_wcet(file_name: str, tasks: List[Task]):
    # Open xml file and extract informations
    tree = ET.parse(file_name)
    root = tree.getroot()
    children = root.findall("CFG")

    for task in tasks:
        for child in children:
            # Get useful tasks only
            if child.attrib['name'] == task.name + "_function":
                attr_list = child.find("ATTRS_LIST")
                wcet_attr = None
                # Look for wcet value
                for attr in attr_list:
                    if attr.attrib['name'] == "WCET":
                        wcet_attr = attr
                # Update task object
                task.set_wcet(int(wcet_attr.attrib['value']) / SCALE)
        # Display object status
        task.display()

if __name__ == '__main__':

    with open('config.json') as config_file:
        data = json.load(config_file)


    # Evaluate hyperperiod length
    periods = [int(ceil(data['tasks'][i]['period']) / SCALE) for i in data['tasks'].keys()]
    hyperperiod = ppcm(periods)
    print(f"Hypeperiod is {hyperperiod} ms.")
    # Update wcet for each task
    print(f"Starting analysis of {data['file']} on tasks: {data['tasks'].keys()}")

    tasks = list()
    # Check which scheduler has been chosen and act accordingly
    if data['algo'] == "RM":

        for i in data['tasks'].keys():
            tasks.append(Task(i, int(data['tasks'][i]['period'])))

        get_wcet(data['file'], tasks)

        scheduler = Scheduler(tasks, hyperperiod)

        if not scheduler.RM_feasibility():
            print("Feasibility condition not verified. No RM schedule with those parameters.")
            exit(-1)
        else:
            print("Feasibility condition verified.")

        if data['preempt'] == True:
            scheduler.schedule_prempt(data['algo'])
        else:
            scheduler.schedule_non_prempt(data['algo'])
        # Draw result in svg file
        draw = Drawer(scheduler.output, tasks, hyperperiod)

        periods.sort()

        draw.draw_schedule(f"RateMonotonic")
    elif data['algo'] == "EDF":

        for i in data['tasks'].keys():
            tasks.append(Task(i, int(data['tasks'][i]['period']), int(data['tasks'][i]['deadline'])))

        get_wcet(data['file'], tasks)

        scheduler = Scheduler(tasks, hyperperiod)

        if data['preempt'] == True:
            scheduler.schedule_prempt(data['algo'])
        else:
            scheduler.schedule_non_prempt(data['algo'])

        draw = Drawer(scheduler.output, tasks, hyperperiod)
        draw.draw_schedule(f"EarliestDeadlineFirst")
    else:
        print("Scheduler {algo} not recognized, please chose either RM or EDF.".format(algo=data['algo']))

