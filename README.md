#ITR SCHEDULER 2021


## Goal

> The goal of this project is to analyze how tasks are scheduled in a simulation of an OIL file 
> 
> This script will analyze the results produced by heptane and will then create an image representing the chosen scheduler
> 
> Here is an overview on how the Program works [overview](./doc/diag_alarachepng.png)
> 

## Usage

> A config file is provided with the script in order to set parameters for the analysis
> 
> Please setup the **config.json** accordingly before launching the script
> 
> In order to run the script, in a terminal type
> 
>  ``python3 main.py ``
>

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
