#ITR SCHEDULER 2021


## Goal

> The goal of this project is to analyze the scheduling of tasks produced by the OIL file in a trampolineRTOS implementation
> 
> This script will analyze the results produced by heptane and will then create an image representing the chosen scheduler
> 
> Here is an overview on how the Program works [overview](diag_alarachepng.png)
> 

## Usage

> In order to run the script, in a terminal type
> 
>  ``python3 collector.py {RM, EDF} -x [heptane-xml-file] -f [functions] ``
>
> Options details :
> 
> Choose a mode from **RM** and **EDF** in order to perform a specific schedulability analysis
> 
> **-x [heptane-xml-file] or --xml_file [heptane-xml-file]** , set this parameter in order to specify which heptane file needs to be anlyzed
> 
> **-t [tasks] or --tasks [tasks]** , specify a function, or a list of functions (separated by a space) that needs to be analyzed. Also provide for each function the period that needs to be considered
> 
    >       e.g.: ..``-t task1 task2 -f period_task1 period_task2``..
>  
> **-p or --preemption_mode** , specifies if preemptive scheduling needs to be considered or not
> 
### Specific options for EDF
>
> **-d [deadlines]** , specifies the deadlines to be considered for EDF scheduling
>
 
## Example

`` python3 collector.py -p 0 RM -x TP_HEPTANE-res.xml -t distance navigation contact -t 1400 1000 1700``

## Results

    Hypeperiod is 11900 ms.
    Starting analysis of TP_HEPTANE-res.xml on ['distance', 'navigation', 'contact'] functions
    NAME : distance ; PERIOD : 140 ; WCET : 29.9
    NAME : navigation ; PERIOD : 100 ; WCET : 37.5
    NAME : contact ; PERIOD : 170 ; WCET : 32.3
    Feasibility condition verified.

> The output image is located inside the same folder of the script.
> 
> Its extensions is **.svg**