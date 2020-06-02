# MPCdesig

  This Python 3 module provides functions for packing and unpacking 
asteroid designations using regular expressions. "Packing" or "unpacking" 
refers to the Minor Planet Center convention described 
[here](https://minorplanetcenter.net/iau/info/PackedDes.html). 
Number designations greater than 619999 can also be packed and unpacked. 

The two main purposes of **MPCdesig** are:
  - to quickly and easily convert a single designation from the command line, 
  for example unpack K08E05V into 2008 EV5 or pack 620000 into ~0000. 
  - to pack or unpack a list of designations, leaving those which are 
  already in the target format unchanged. This is especially helpful when you 
  regularly work with lists of asteroids gathered from different sources, which 
  likely use different formats, and you want to tabulate all targets with the 
  same packed or unpacked format. 
  
The module is more easily used as a script, i.e. directly from the console with
a command specifying your input designation or the name of a file containing 
designations (see the Examples section below). The output simply goes to stdout 
and can easily be redirected into a file. While this is how I have used the 
module, you may also find some of the functions useful for your own scripts or 
modules.


## Requirements

- (Python 3) argparse, numpy, re, sys  


## Examples

The following command packs the provisional designation "2008 EV5" directly from
the console:
```
python MPCdesig.py -p -d "2008 EV5"
K08E05V
```
Accepted field separators for input provisional designations are " ", "_", "-", 
or none, i.e. 2008EV5 is also valid. If you have several versions of Python 
installed on your computer and Python 3 is not the default one, try:
```
python3 MPCdesig.py -p -d "2008 EV5"
K08E05V
```
The quotes are necessary for input provisional designations with more than one 
field and packed designations starting with the character "~", e.g. ~0000. 


To unpack "K08E05V" we use the -u option: 
```
python MPCdesig.py -u -d K0805V -s "_"
2008_EV5
```
Here we specified "_" as the separator with the -s option. By default, the 
field separator is the SPACE character. If you prefer not to have any 
separator on your provisional designations, simply input an empty string: 
```
python MPCdesig.py -u -d K08E05V -s ""
2008EV5
```
To see how the module deals with a list of designations contained in a file, 
I recommend both packing and unpacking the file **example_list.txt**. After 
examining the file, run both
``` 
python MPCdesig.py -f example_list.txt -u 
```
and 
``` 
python MPCdesig.py -f example_list.txt -p 
```
and compare the outputs with the input. 
You can see that for input designations that are already unpacked (e.g. the 
first three), the output is the same, either the unpacked form without 
parentheses and without the name or any other strings given afterwards, or the 
1 padded with four 0s. 


## Caveat/Warning

The pack() and unpack() functions will try to convert the first substring that 
is matched on every line so they assume that each line corresponds to one and 
only one asteroid. This does not mean that each line cannot contain more than 
one designations, e.g. "(341843) 2008 EV5" would be a valid input line. In such
cases, however, the numbered designation is packed or unpacked. 

Although I have tested the module before release, you will surely find bugs and 
cases that should be handled correctly but for which the module will not work. 
Please contact me and I'll do my best to implement fixes quickly, but of course 
you are also welcome to implement them yourself. 

Victor Ali Lagoa
vmalilagoa@gmail.com
(Munich, May 2020)
 
