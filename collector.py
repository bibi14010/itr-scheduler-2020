import argparse
import xml.etree.ElementTree as ET
from math import gcd, ceil
from drawer import Drawer
from scheduler import *
from typing import List

SCALE = 10


def ppcm(list: List[int]):
    lcm = list[0]
    for i in list[1:]:
        lcm = lcm * i // gcd(lcm, i)
    return lcm


def get_wcet(file_name: str, functions: List[Task]):
    # Open xml file and extract informations
    tree = ET.parse(file_name)
    root = tree.getroot()
    children = root.findall("CFG")

    for function in functions:
        for child in children:
            # Get usefull functions only
            if child.attrib['name'] == function.name + "_function":
                attr_list = child.find("ATTRS_LIST")
                wcet_attr = None
                # Look for wcet value
                for attr in attr_list:
                    if attr.attrib['name'] == "WCET":
                        wcet_attr = attr
                # Update Function object
                function.set_wcet(int(wcet_attr.attrib['value']) / SCALE)
        # Display object status
        function.display()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    rm_parser = subparser.add_parser('RM')
    rm_parser.set_defaults(which="RM")
    rm_parser.add_argument("-x", "--xml_file", required=True, help="XML file to analyse. e-g: -x TP_HEPTANE-rex.xml.")
    rm_parser.add_argument("-f", "--functions", required=True, nargs="+", help="Name of the functions to be considered "
                                                                               "first, then their respective periods in "
                                                                               "ms. e-g: -f fct1 fct2 -f fct1_t fct2_t ",
                           action='append')

    edf_parser = subparser.add_parser("EDF")
    edf_parser.set_defaults(which="EDF")
    edf_parser.add_argument("-x", "--xml_file", required=True, help="XML file to analyse. e-g: -x TP_HEPTANE-rex.xml.")
    edf_parser.add_argument("-f", "--functions", required=True, nargs="+", help="Name of the functions to be considered"
                                                                                " first, then their respective periods in "
                                                                                "ms. e-g: -f fct1 fct2 -f fct1_t fct2_t ",
                            action='append')
    edf_parser.add_argument("-d", "--deadlines", required=True, nargs="+",
                            help="Respective deadlines of the functions.")

    parser.add_argument("-p", "--preemption_mode", required=True, help="0 or 1 . 0 for preemptive scheduling "
                                                                       "and 1 for not preemptive one.")

    args = vars(parser.parse_args())

    # Check if all functions have all their informations
    if len(args['functions']) < 2 or (len(args['functions'][0]) != len(args['functions'][1])):
        print("Missing parameters. example of command :python3 collector.py -x myfile.xml -f fct1 fct2 -f 100 "
              "200")
        exit(-1)

    # Total number of analyzed functions
    number = len(args['functions'][0])
    names = args['functions'][0]
    periods = [ceil(int(i) / SCALE) for i in args['functions'][1]]
    # If edf is chosen, set deadlines
    deadlines = None
    if args.get("which") == "EDF":
        deadlines = [int(i) for i in args['deadlines']]

    # Create Function objects
    functions = list()
    for index in range(number):
        if args.get("which") == "EDF":
            functions.append(Task(names[index], int(periods[index]), int(deadlines[index])))
        elif args.get("which") == "RM":
            functions.append(Task(names[index], int(periods[index])))
    # Get Hyperperiod time
    hyperperiod = ppcm(periods)
    print(f"Hypeperiod is {hyperperiod} ms.")
    # Upadte wcet for each functions
    print(f"Starting analysis of {args['xml_file']} on {names} functions")
    get_wcet(args['xml_file'], functions)

    # RM schedule
    if args.get("which") == "RM":
        scheduler = RateMonotonic(functions, hyperperiod)
        if not scheduler.RM_feasibility():
            print("Feasibility condition not verified. No RM schedule with those parameters.")
            exit(-1)
        else:
            print("Feasibility condition verified.")
        if int(args["preemption_mode"]) == 0:
            scheduler.schedule_non_prempt()
        elif int(args["preemption_mode"]) == 1:
            scheduler.schedule_prempt()
        # Draw result in svg file
        draw = Drawer(scheduler.RM, periods, hyperperiod)
        periods.sort()
        draw.draw_schedule(f"RateMonotonic_{args['preemption_mode']}")
    # EDF Schedule
    elif args.get("which") == "EDF":
        scheduler = EarliestDeadlineFirst(functions, hyperperiod)
        if int(args["preemption_mode"]) == 0:
            scheduler.schedule_non_prempt()
        elif int(args["preemption_mode"]) == 1:
            scheduler.schedule_prempt()
        draw = Drawer(scheduler.EDF, periods, hyperperiod)
        draw.draw_schedule(f"EarliestDeadlineFirst_{args['preemption_mode']}")

    exit(0)
