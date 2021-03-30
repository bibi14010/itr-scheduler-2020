import argparse
import xml.etree.ElementTree as ET
from function import Function
from math import gcd, ceil
from drawer import Drawer
from scheduler import *

SCALE = 10


# Source : stackoverflow.com | I'm not very good at math :)
def ppcm(list: list[int]):
    lcm = list[0]
    for i in list[1:]:
        lcm = lcm * i // gcd(lcm, i)
    return lcm


def get_wcet(file_name: str, functions: list[Function]):
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
    parser.add_argument("-x", "--xml_file", required=True, help="XML file to analyse. e-g: -x TP_HEPTANE-rex.xml.")
    parser.add_argument("-f", "--functions", required=True, nargs="+", help="Name of the functions to be considered "
                                                                            "first, then their respective periods in "
                                                                            "ms. e-g: -f fct1 fct2 -f fct1_t fct2_t ",
                        action='append')
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
    # Create Function objects
    functions = list()
    for index in range(number):
        functions.append(Function(names[index], int(periods[index])))

    # Get Hyperperiod time
    hyperperiod = ppcm(periods)
    print(f"Hypeperiod is {hyperperiod} ms.")
    # Upadte wcet for each functions
    print(f"Starting analysis of {args['xml_file']} on {names} functions")
    get_wcet(args['xml_file'], functions)

    # RM schedule
    scheduler = RateMonotonic(functions, hyperperiod)
    if not scheduler.RM_feasibility():
        print("Feasibility condition not verified. No RM schedule with those parameters.")
        exit(-1)
    scheduler.Schedule()

    # TODO Make EDF scheduler

    periods.sort()
    draw = Drawer(scheduler.RM, periods, hyperperiod)
    draw.draw_schedule("RateMonotonic")
