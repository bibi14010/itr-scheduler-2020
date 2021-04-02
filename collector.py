import argparse
import xml.etree.ElementTree as ET
from math import gcd, ceil
from drawer import Drawer
from scheduler import Scheduler
from typing import List
from task import Task
SCALE = 10


def ppcm(list: List[int]):
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

def argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--preemption_mode", help="If activated, it enables schedulability analysis by taking in consideretation preemptions")

    subparser = parser.add_subparsers()

    rm_parser = subparser.add_parser('RM')
    rm_parser.set_defaults(which="RM")
    rm_parser.add_argument("-x", "--xml_file", required=True, help="XML file to analyse. e-g: -x TP_HEPTANE-rex.xml.")
    rm_parser.add_argument("-t", "--tasks", required=True, nargs="+", help="Name of the tasks to be considered "
                                                                               "first, then their respective periods in "
                                                                               "ms. e-g: -f fct1 fct2 -f fct1_t fct2_t ",
                           action='append')

    edf_parser = subparser.add_parser("EDF")
    edf_parser.set_defaults(which="EDF")
    edf_parser.add_argument("-x", "--xml_file", required=True, help="XML file to analyse. e-g: -x TP_HEPTANE-rex.xml.")
    edf_parser.add_argument("-t", "--tasks", required=True, nargs="+", help="Name of the tasks to be considered"
                                                                                " first, then their respective periods in "
                                                                                "ms. e-g: -f fct1 fct2 -f fct1_t fct2_t ",
                            action='append')
    edf_parser.add_argument("-d", "--deadlines", required=True, nargs="+",
                            help="Respective deadlines of the tasks.")


    return vars(parser.parse_args())

if __name__ == '__main__':


    args = argparser()

    # Check if all tasks have all their informations
    if len(args['tasks']) < 2 or (len(args['tasks'][0]) != len(args['tasks'][1])):
        print("Missing parameters. example of command :python3 collector.py -x myfile.xml -f fct1 fct2 -f 100 "
              "200")
        exit(-1)

    # Total number of analyzed tasks
    number = len(args['tasks'][0])
    names = args['tasks'][0]
    periods = [ceil(int(i) / SCALE) for i in args['tasks'][1]]
    # If edf is chosen, set deadlines
    deadlines = None
    if args.get("which") == "EDF":
        deadlines = [int(i) for i in args['deadlines']]

    # Create task objects
    tasks = list()
    for index in range(number):
        if args.get("which") == "EDF":
            tasks.append(Task(names[index], int(periods[index]), int(deadlines[index])))
        elif args.get("which") == "RM":
            tasks.append(Task(names[index], int(periods[index])))
    # Get Hyperperiod time
    hyperperiod = ppcm(periods)
    print(f"Hypeperiod is {hyperperiod} ms.")
    # Upadte wcet for each task
    print(f"Starting analysis of {args['xml_file']} on {names} tasks")
    get_wcet(args['xml_file'], tasks)

    # RM schedule
    if args.get("which") == "RM":
        scheduler = Scheduler(tasks, hyperperiod)
        if not scheduler.RM_feasibility():
            print("Feasibility condition not verified. No RM schedule with those parameters.")
            exit(-1)
        else:
            print("Feasibility condition verified.")
        if int(args["preemption_mode"]) == 0:
            scheduler.schedule_non_prempt('RM')
        elif int(args["preemption_mode"]) == 1:
            scheduler.schedule_prempt('RM')
        # Draw result in svg file
        draw = Drawer(scheduler.RM, periods, hyperperiod)
        periods.sort()
        draw.draw_schedule(f"RateMonotonic_{args['preemption_mode']}")
    # EDF Schedule
    elif args.get("which") == "EDF":
        scheduler = Scheduler(tasks, hyperperiod)
        if int(args["preemption_mode"]) == 0:
            scheduler.schedule_non_prempt('EDF')
        elif int(args["preemption_mode"]) == 1:
            scheduler.schedule_prempt('EDF')
        draw = Drawer(scheduler.EDF, periods, hyperperiod)
        draw.draw_schedule(f"EarliestDeadlineFirst_{args['preemption_mode']}")

