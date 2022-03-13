"""
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
module, you may also find some functions useful for your own scripts or 
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
one designation, e.g. "(341843) 2008 EV5" would be a valid input line. In such
cases, however, the numbered designation is packed or unpacked. 

Although I have tested the module before release, you will surely find bugs and 
cases that should be handled correctly but for which the module will not work. 
Please contact me, and I'll do my best to implement fixes quickly. Of course,
you are also welcome to implement them yourself. 

Victor Ali Lagoa
vmalilagoa@gmail.com
(Munich, May 2020)
 
"""

import sys

version_string = ".".join(map(str, sys.version_info[:3]))

try:
    import numpy as np
    import re
    import argparse

except ModuleNotFoundError:
    sys.exit(f"\n*****\npython {version_string}: {sys.exc_info()[1]}\n*****\n")

####################################################
# Argument parser, helpful for parsing input arguments when running as a script
#
argParserMPC = argparse.ArgumentParser(
    description="""
  Functions for packing and unpacking asteroid designations with different
formats using regular expressions in Python 3. "Packing" refers to the Minor
Planet Center convention. The "new" packing format for numbered designations 
greater than 619999 are also handled. It also works as a script directly 
called from the command line. 

  Example:
  We can pack the provisional designation "2008 EV5" into "K08E05V". Accepted
  field separators for input provisional designations are " ", "_", "-" or none,
  i.e. 2008EV5 is also a valid input string.

* Requirements (Python 3): numpy, re, sys and argparse modules
    """,
    epilog='May 2020. Victor Ali Lagoa (vmalilagoa@gmail.com)'
)

argParserMPC.add_argument(
    '-d', dest='desig', type=str,
    help='An input asteroid designation')

argParserMPC.add_argument(
    '-f', dest='filename', type=str,
    help='File containing asteroid designations arranged in a single column')

argParserMPC.add_argument(
    '-p', dest='pack', action="store_true",
    help='Pack the input')

argParserMPC.add_argument(
    '-s', dest='separator', default=" ",
    help="""
Separator character for provis. designations.\n
Default '_' (e.g. 2008_EV5)""")

argParserMPC.add_argument(
    '-u', dest='unpack', action="store_true",
    help='Unpack the input')

################################################################################
# Dictionaries to convert to and from packed provisional designations
#

p2unp_prov = dict([('I', '18'), ('J', '19'), ('K', '20')])
unp2p_prov = dict([('18', 'I'), ('19', 'J'), ('20', 'K')])

# packed numbered to unpacked numbered and vice versa
p2unp_num = dict([('A', '10'), ('B', '11'), ('C', '12'), ('D', '13'),
                  ('E', '14'), ('F', '15'), ('G', '16'), ('H', '17'),
                  ('I', '18'), ('J', '19'), ('K', '20'), ('L', '21'),
                  ('M', '22'), ('N', '23'), ('O', '24'), ('P', '25'),
                  ('Q', '26'), ('R', '27'), ('S', '28'), ('T', '29'),
                  ('U', '30'), ('V', '31'), ('W', '32'), ('X', '33'),
                  ('Y', '34'), ('Z', '35'), ('a', '36'), ('b', '37'),
                  ('c', '38'), ('d', '39'), ('e', '40'), ('f', '41'),
                  ('g', '42'), ('h', '43'), ('i', '44'), ('j', '45'),
                  ('k', '46'), ('l', '47'), ('m', '48'), ('n', '49'),
                  ('o', '50'), ('p', '51'), ('q', '52'), ('r', '53'),
                  ('s', '54'), ('t', '55'), ('u', '56'), ('v', '57'),
                  ('w', '58'), ('x', '59'), ('y', '60'), ('z', '61')])

unp2p_num = dict([('00', '0'),
                  ('10', 'A'), ('11', 'B'), ('12', 'C'), ('13', 'D'),
                  ('14', 'E'), ('15', 'F'), ('16', 'G'), ('17', 'H'),
                  ('18', 'I'), ('19', 'J'), ('20', 'K'), ('21', 'L'),
                  ('22', 'M'), ('23', 'N'), ('24', 'O'), ('25', 'P'),
                  ('26', 'Q'), ('27', 'R'), ('28', 'S'), ('29', 'T'),
                  ('30', 'U'), ('31', 'V'), ('32', 'W'), ('33', 'X'),
                  ('34', 'Y'), ('35', 'Z'), ('36', 'a'), ('37', 'b'),
                  ('38', 'c'), ('39', 'd'), ('40', 'e'), ('41', 'f'),
                  ('42', 'g'), ('43', 'h'), ('44', 'i'), ('45', 'j'),
                  ('46', 'k'), ('47', 'l'), ('48', 'm'), ('49', 'n'),
                  ('50', 'o'), ('51', 'p'), ('52', 'q'), ('53', 'r'),
                  ('54', 's'), ('55', 't'), ('56', 'u'), ('57', 'v'),
                  ('58', 'w'), ('59', 'x'), ('60', 'y'), ('61', 'z')])

################################################################################
# Compiled regular expressions
#

re_numbered_designation = re.compile(r"^[(]?(\d{1,8})[)]?\b")

re_packed_numbered_designation = re.compile(r"\b([~a-zA-Z])(\d{4})\b")
# matches e.g. A3434, g3434
# but not A343 or g34343

# Capture the first group of numbers before the last four:
re_provisional_designation = \
    re.compile(r"\b(\d{4})([- _]?)([a-zA-Z]{2})(\d*)\b")
re_packed_provisional_designation = \
    re.compile(r"\b([IJK])(\d{2})([A-Z])([a-zA-Z0-9])(\d)([A-Z])\b")
re_survey = re.compile(r"\b(\d{4})[- _]([PT])-([L123])\b")
re_packed_survey = re.compile(r"\b([PT])([L123])S(\d{4})\b")
re6digits = re.compile(r"\b(\d{2,})(\d{4})\b")
rePackedLong = re.compile(r"(~)([0-9a-zA-Z]{4})\b")


###############################################################################
# Functions
#
# Most functions belong to two types: some check, some pack or unpack 
#

def to_str(input_desig):
    """
    Remove the leading and trailing space characters from the input string 
    
    *Return: string
    """
    return str(input_desig).strip()


def is_valid_survey_designation(designation: str) -> bool:
    """
    Check whether the input designation is a valid survey designation (packed 
    or unpacked). It simply calls check_packed_unpacked() with the correct 
    compiled regular expressions in order to improve legibility and avoid 
    errors. See also check_valid_prov_desig().

    *Input: asteroid designation (string or integer)

    *Return: boolean
    """

    try:
        designation: str = str(designation).strip()
        return is_packed_or_unpacked(designation, re_survey, re_packed_survey)
    except AttributeError:
        return False


def is_unpacked_survey_designation(designation: str) -> bool:
    try:
        designation: str = designation.strip()
        return designation_matches_compiled_re(designation, re_survey)
    except AttributeError:
        return False


def is_packed_survey_designation(designation: str) -> bool:
    try:
        designation: str = designation.strip()
        return designation_matches_compiled_re(designation, re_packed_survey)
    except AttributeError:
        return False


def check_valid_num_desig(designation: str) -> bool:
    """
    Check whether the input string or number is a valid numbered designation 
    (whether packed or unpacked), e.g. (1) Ceres, (1), 1, 00001, A1203, 101203,
    a1203, 361203, ~232s are all valid numbered designations. Unlike 
    check_valid_prov_desig() or check_valid_surv_desig(), this does not simply 
    call check_packed_unpacked() because that approach would not work well
    with numbered designations (the re_numbered_designation will match anything that contains at 
    least one digit).

    Names or anything written after a matched designation are ignored except
    when they lead to one or more matches. For example, "(1) Ceres" will return
    True, but "(1) Cer3s" will not, because the 3 will also be matched by the 
    regular expression searching for numbered designations, and I assume this
    should not happen. This criterion is admittedly arbitrary, but it can help
    detect errors in an input list, for example if there are missing carriage 
    returns. This also assumes that no "given name" (Ceres, Pallas, ...) should
    be or contain a number, but this could be wrong (tbd). 

    *Input: string or integer

    *Return: boolean
    """

    try:
        designation = str(designation).strip()
    except AttributeError:
        # Is it an array or a list?
        return False

    # can we transform it into a single string with digits?
    if designation.isdigit():
        if designation_matches_compiled_re(designation, re_numbered_designation):
            return True
        else:
            # It should not be longer than 8 digit characters long (in 2020!)
            return False
    elif designation_matches_compiled_re(designation, rePackedLong):
        return True
    elif designation_matches_compiled_re(designation, re_packed_numbered_designation):
        return True
    elif designation_matches_compiled_re(designation, re_numbered_designation):
        # => must still be of the type "(1) Ceres"
        return True
    else:
        return False


def is_valid_provisional_designation(designation: str) -> bool:
    """
    Check whether the input string or number is a valid provisional designation 
    (whether packed or unpacked), e.g. 2008 EV5, 2008EV5, ... or K08E05V. It 
    simply calls check_packed_unpacked() with the correct compiled regular 
    expressions in order to improve legibility and avoid errors. 
    See also check_valid_surv_desig() and compare with check_valid_num_desig().

    *Input: an asteroid designation (string)

    *Return: boolean
    """

    try:
        designation: str = str(designation).strip()
        return is_packed_or_unpacked(designation,
                                     re_provisional_designation,
                                     re_packed_provisional_designation)
    except AttributeError:
        return False


def check_valid_desig(designation):
    """
    This function checks whether the input is a valid asteroid designation. It 
    simply encapsulates calls to check_valid_prov_desig(), 
    check_valid_surv_desig() and check_valid_num_desig(). 

    *Input: an asteroid designation (string or integer)

    *Return: boolean
    """

    if is_valid_provisional_designation(designation):
        return True
    elif is_valid_survey_designation(designation):
        return True
    elif check_valid_num_desig(designation):
        return True
    else:
        return False


def designation_matches_compiled_re(designation: str, compiled_re: re) -> bool:
    """
    Check whether the input asteroid designation is matched by the input 
    compiled regular expressions.

    *Input: an asteroid designation (string or integer)
    *Input: a compiled regular expression

    *Return: boolean
    """

    it_matches = False  # by default

    try:
        designation: str = str(designation).strip()
    except AttributeError:
        return False

    matches = compiled_re.findall(designation)
    if matches and len(matches) == 1:
        # We consider more than one match suspicious (the input
        # should contain only one valid asteroid designation).
        it_matches = True

    return it_matches


def is_packed_or_unpacked(designation: str,
                          packed_compiled_re: re,
                          unpacked_compiled_re: re) -> bool:
    """
    Check if an input designation is a valid one according to the input 
    compiled regular expressions (they should match the type of designation you
    are trying to verify, e.g. re_numbered_designation and re_packed_numbered_designation for numbered designations).
    See also check_valid_num_desig() or check_valid_prov_desig(). 

    *Input: input_desig is a string or an integer
    *Input: compPacked is a compiled regular expression conceived to find a 
    certain type of packed designation, e.g. re_numbered_designation or reProv
    *Input: compUnpacked is a compiled regular expression conceived to find a 
    certain type of unpacked designation, e.g. re_packed_numbered_designation or reProvPacked

    *Return: boolean
    """

    return designation_matches_compiled_re(designation, packed_compiled_re) or designation_matches_compiled_re(
        designation, unpacked_compiled_re)


def check_single_unp_prov(input_desig):
    """
    Check if the input both contain a match for a valid number designation
    and a provisional designation, e.g. "(341843) 2008 EV5". "2008 EV5" will 
    produce the same kind of match, so we must compare the matched number with
    the first part of the provisional designation. 

    *Input: an asteroid designation (string or int)

    *Return: boolean
    """
    final_c = False

    input_d = str(input_desig).strip()
    if is_valid_provisional_designation(input_d) and check_valid_num_desig(input_d):

        fa_match = re_provisional_designation.findall(input_d)
        if fa_match:
            first_part = fa_match[0][0]
        else:
            return final_c
        fa_match = re_numbered_designation.findall(input_d)
        if fa_match:
            num = fa_match[0]
        else:
            return final_c

        if num == first_part:
            final_c = True

    return final_c


def pack_base_62(num_desig):
    """
    Pack a numbered designation greater than 619999 following the Minor 
    Planet Center's description.

    *Input: a valid numbered designation (string or integer)
    *Return: a string with the corresponding packed designation or an error 
    message
    """

    try:
        num_int = int(num_desig) - 620000
        resul = ""
    except ValueError:
        return "pack_base_62(): Error. {0} not a valid num. designation".format(
            num_desig)

    for i in range(4):
        q = num_int // 62
        rem = num_int % 62
        if rem > 9:
            rem = "{0}".format(unp2p_num[str(rem)])
        num_int = q
        resul = str(rem) + resul
    return "~" + "{0}".format(resul)


def unpack_base_62(packed_desig):
    """
    Unpack a numbered designation greater than 619999 (e.g. "~12z3") following 
    the Minor Planet Center's specification. 

    *Input: a valid packed numbered designation (string or integer)

    *Return: string with the corresponding unpacked designation or an error 
    message
    """
    error_message = "Error. {0} is not a valid packed long numbered designation".format(
        packed_desig)

    if not (designation_matches_compiled_re(packed_desig, rePackedLong)):
        return "unpack_base_62(): {0}".format(error_message)

    suma = 0
    packed_desig = str(packed_desig).strip()
    for i in range(4):
        pos_i = packed_desig[1 + i]
        if pos_i.isdigit():
            num = int(pos_i)
        else:
            num = int(p2unp_num[packed_desig[1 + i]])
        suma += num * np.power(62, 3 - i)
    return str(suma + 620000)


def pack_num(input_desig):
    """
    Pack an input numbered asteroid designation, e.g. (1) Ceres, or 1 Ceres. If
    the input is already a valid numbered designation it returns it back. 

    *Input: a valid asteroid number designation (string or a number)

    *Return: string with the MPC-packed designation or an error message
    """

    error_message = """pack_num() error: '{0}' not valid for packing""".format(
        input_desig)

    input_str = to_str(input_desig)
    if check_valid_num_desig(input_str):

        try:
            # We remove parentheses
            num = int(re.sub("[\(\)]", "", input_str.split(" ")[0]))
            if num > 619999:
                # We pack it with the base 62 notation
                return pack_base_62(num)

            elif num > 99999:
                # regex for the two groups to pack the first two digits:
                fa_long = re6digits.findall(input_str)
                pref = unp2p_num[fa_long[0][0]]
                return pref + fa_long[0][1]
            else:
                # it requires padding
                return "{0:05d}".format(num)

        except:
            # the int() failed, so it should be a valid packed designation
            return input_desig
    else:
        # print(error_message)
        return error_message


def unpack_num(input_desig):
    """
    Return the unpacked version of the input number designation if it is
    a valid packed one, or the very input if it is a valid unpacked one.
    It returns an error message otherwise.

    *Input: asteroid designation (string or int)

    *Return: unpacked designation or error message
    """

    error_message = """unpack_num(): Error. '{0}' not valid for unpacking""".format(
        input_desig)

    input_str = to_str(input_desig)
    if check_valid_num_desig(input_str):
        fa_match = rePackedLong.findall(input_str)
        if fa_match and len(fa_match) == 1:
            return unpack_base_62(input_str)
        else:
            fa_match = re_packed_numbered_designation.findall(input_desig)
            if fa_match and len(fa_match) == 1:
                frst = p2unp_num[fa_match[0][0]]
                return frst + fa_match[0][1]
            else:
                fa_match = re_numbered_designation.findall(input_desig)
                return "{0:d}".format(int(fa_match[0]))

    else:
        # print(error_message)
        return error_message


def pack_prov(input_desig):
    """Pack an input designation if it is a valid provisional asteroid 
    designation. For example, 

    input       output
    ---------------------
    2008_SO254  K08SP4O
    2008 SO254  K08SP4O
    2008-SO254  K08SP4O
    2008SO254   K08SP4O

    If it is already a packed provisional designation, it outputs it. 
    Otherwise, it returns an error message. 

    *Input: an asteroid designation (string or integer)

    *Return: a string with the packed form of the input or an error message
    """

    error_message = """pack_prov(): Error. '{0}' not valid for packing""".format(
        input_desig)

    input_str = to_str(input_desig)
    if is_valid_provisional_designation(input_str):

        fa_match = re_provisional_designation.findall(input_str)
        if fa_match and len(fa_match) == 1:
            # It must have worked:
            # so fa_match must be of the form:
            # [('1923', '-', 'AG', '342')]
            #
            # year 1923 -> frst=19, scnd=23
            frst = unp2p_prov[fa_match[0][0][0:2]]
            scnd = fa_match[0][0][2:]

            # half-month period, e.g. ABnumb -> ApackedB
            frst_hm = fa_match[0][2][0]
            scnd_hm = fa_match[0][2][1]

            num_str = fa_match[0][3]
            if len(num_str) == 0:
                mid = "00"
            elif len(num_str) > 2:
                # We pack the two first numbers
                mid = unp2p_num[num_str[0:2]] + num_str[2]
            else:
                mid = "{0:02d}".format(int(num_str))

            return frst + scnd + frst_hm + mid + scnd_hm

        else:
            # It might be already packed:
            fa_match = re_packed_provisional_designation.findall(input_str)
            if fa_match and len(fa_match) == 1:
                return input_str
            else:
                return error_message
    else:
        # print(error_message)
        return error_message


def unpack_prov(input_desig, separator):
    """Return the unpacked version of the input provisional designation if 
    it is a valid packed one, or the very input if it is a valid unpacked one.
    
    *Input: an asteroid designation (string or integer)
    *Input: a character that will be used as separator in the output provisional
    designation

    *Return: unpacked provisional designation (str) or an error message
    """

    error_message = """unpack_prov(): Error. '{0}' not valid for unpacking""".format(
        input_desig)

    input_str = re.sub("[ _]", "-", to_str(input_desig), count=1)
    if is_valid_provisional_designation(input_str):
        fa_match = re_provisional_designation.findall(input_str)
        if fa_match and len(fa_match) == 1:
            # it is a valid provisional designation, already unpacked, so
            # we just insert the input separator
            return fa_match[0][0] + separator + fa_match[0][2] + fa_match[0][3]

        fa_match = re_packed_provisional_designation.findall(input_desig)
        frst_y = p2unp_prov[fa_match[0][0]]
        scnd_y = fa_match[0][1]
        frst_fn = fa_match[0][2]
        scnd_fn = fa_match[0][5]
        try:
            n1 = int(fa_match[0][3])
            if n1 < 1:
                n1 = ""
            else:
                n1 = str(n1)
        except:
            n1 = p2unp_num[fa_match[0][3][0]]

        n2 = fa_match[0][4]
        if int(fa_match[0][4]) < 1:
            n2 = ""

        return frst_y + scnd_y + separator + frst_fn + scnd_fn + n1 + n2
    else:
        # print(error_message)
        return error_message


def pack_survey_desig(input_desig):
    """
    Pack a special survey asteroid designation.

    *Input: an asteroid designation

    *Return: a string with the packed designation or an error message
    """

    error_message = "{0} is not a valid special survey designation".format(input_desig)

    des = to_str(input_desig)

    if des.isdigit():
        return "pack_survey_desig(): Error. {0}".format(error_message)

    try:
        numbers = des[0:4]
        lett1 = des[5]
        lett2 = des[7]
        return lett1 + lett2 + "S" + numbers
    except:
        return "pack_survey_desig(): Error. {0}".format(error_message)


def unpack_survey_desig(input_desig):
    """
    Unpack a special survey asteroid designation.

    *Input: an asteroid designation

    *Return: a string with the packed designation or an error message
    """

    error_message = "{0} is not a valid special survey designation".format(input_desig)

    des = to_str(input_desig)

    if des.isdigit():
        # This should not happen, by definition
        return "unpack_survey_desig(): Error. {0}".format(error_message)

    try:
        numbers = des[3:]
        lett1 = des[0]
        lett2 = des[1]
        return numbers + " " + lett1 + "-" + lett2
    except:
        return "unpack_survey_desig(): Error. {0}".format(error_message)


def unpack(input_desig, separator):
    """
    Call the necessary function for unpacking the input after some checks. 
    If the input designation is already a valid unpacked designation, it 
    returns it. 

    *Input: an asteroid designation (string or int)
    *Input: character to be used to separate provisional designations

    *Return: an unpacked asteroid designation (string) or an error message
    """

    error_message = """unpack(): Error. '{0}' not valid for unpacking""".format(
        input_desig)

    input_d = to_str(input_desig)

    single_provis = check_single_unp_prov(input_d)

    if is_valid_survey_designation(input_d):
        if is_unpacked_survey_designation(input_d):
            return input_d
        else:
            return unpack_survey_desig(input_d)
    elif check_valid_num_desig(input_d) and not single_provis:
        return unpack_num(input_d)
    elif is_valid_provisional_designation(input_d):
        return unpack_prov(input_d, str(separator))

    else:
        # print(error_message)
        return error_message


def pack(input_desig):
    """
    Call the necessary function for packing the input designation after some 
    checks. If the input designation is already a valid packed designation, it 
    returns it. 

    *Input: an asteroid designation (string or int)

    *Return: an unpacked asteroid designation (string) or error message
    """

    error_message = """pack(): Error. '{0}' not valid for packing""".format(input_desig)

    input_d = to_str(input_desig)

    single_provis = check_single_unp_prov(input_d)

    if is_valid_survey_designation(input_d):
        return pack_survey_desig(input_d)
    elif check_valid_num_desig(input_d) and not (single_provis):
        return pack_num(input_d)
    elif is_valid_provisional_designation(input_d):
        return pack_prov(input_d)
    else:
        return error_message


def convert(inp, p_or_unp):
    """
    Pack or unpack the input designation or file with designations. This is 
    simply the main() function but without using the argument parser and a 
    hard-coded default separator (the underscore character). This means that 
    the second argument must exactly be either "pack" or "unpack", otherwise it 
    will not work. Another issue is that it also does not have the same error 
    handling as the main() function, so I do not recommend its use as a black 
    box. However, it could be a good template for creating your own "convert" 
    function(s) in your own script(s) or module(s). 

    *Input: asteroid designation or a file with asteroid designations
    *Input: "pack" or "unpack" (no other strings are valid)
     
    *Return: string with output or an error message
    """

    input_ = str(inp)
    if len(input_) > 0 and check_valid_desig(input_):
        designations = [input_]
        # Create a list with the input so that we can iterate over it
    else:
        try:
            # Perhaps it is an input filename, not a designation
            myfile = open(input_, 'r')
            designations = myfile.readlines()
            myfile.close()
        except IOError:
            print("convert(): Error. Did not find file '{0}'".format(input_))
            designations = []
            # We still need an empty list to iterate over next

    for designation in designations:
        if len(designation.split()) < 1:
            print("convert(): Warning. Input is an empty line")
        else:
            if p_or_unp == "pack":
                print(pack(designation.replace("\n", "")))
            elif p_or_unp == "unpack":
                print(unpack(designation.replace("\n", ""), "_"))
            else:
                print("convert(): Error. 2nd arg. must be 'pack' or 'unpack'")


def main():
    parsed = argParserMPC.parse_args()

    if not (parsed.pack or parsed.unpack):
        print("main(): Error. Either -p or -u must be used")
        sys.exit(-1)

    if parsed.desig:
        # if we parsed a designation, we have a list with one element
        designations = [parsed.desig]

    elif parsed.filename:
        filename = str(parsed.filename)
        # we expect a file with many desigs
        try:
            openfile = open(filename, 'r')
            designations = openfile.readlines()
            openfile.close()
        except IOError:
            print("main(): Error. Did not find file '{0}'\n".format(filename))
            sys.exit(-2)
    else:
        print("main(): Error. Input a designation [-d] or a file name [-f]")
        sys.exit(-3)

    #
    # If we made it here, we have at least one designation to try to convert
    #
    for designation in designations:
        if len(designation.split()) < 1:
            print("main(): Warning. Empty line")
        else:
            if parsed.pack:
                print(pack(designation.replace("\n", "")))
            elif parsed.unpack:
                print(unpack(designation.replace("\n", ""), parsed.separator))


if __name__ == "__main__":
    # execute only if run as a script
    main()
