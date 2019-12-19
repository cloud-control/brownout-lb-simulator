## Cloning simulator

Type `python simulator.py --help` for detailed help on the available command line arguments.

#### Overview of arcitecture

`simulator.py` runs a single simulation for the given input parameters and supplied scenario file.
 
The scenario files in `scenarios/` adds servers of desired types, and sets meta-parameters for the 
simulation. 
 
Larger simulation of parameter sweeps is most easily done by scripting. An examples on how to run the 
simulator in a scripted fashion is available in `sim_example.py` and its corresponding scenario
file `scenarios/clone-example-py`.
