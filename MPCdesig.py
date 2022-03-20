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
  regularly work with lists of asteroids gathered from different sources that
  use different formats.
  
The module is more easily used as a script, i.e. directly from the console with
a command specifying your input designation or the name of a file containing 
designations (see examples below). The output simply goes to stdout
and can easily be redirected into a file. While this is how I have used the 
module, you may also find some functions useful for your own scripts or 
modules.


## Requirements

- (Python 3) argparse, numpy, re, sys  


## Examples

The following command packs the provisional designation "2008 EV5":
```
python MPCdesig.py -p -d "2008 EV5"
K08E05V
```
Accepted field separators for input provisional designations are " ", "_"
and "-". Provisional designations without separator, e.g. 2008EV5, are also
parsed.

If you have several versions of Python installed on your computer and Python
3 is not the default one, try:
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
    from typing import Union

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
    '-d', dest='designation', type=str,
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
re_packed_long = re.compile(r"(~)([0-9a-zA-Z]{4})\b")


###############################################################################
# Functions
#
# Most functions belong to two types: some check, some pack or unpack 
#

def to_stripped_string(designation: str):
    """
    Cast to string if possible and remove the leading and trailing space
    characters from the input string
    
    *Return: string
    """
    return str(designation).strip()


def is_valid_survey_designation(designation: str) -> bool:
    """
    Check whether the input designation is a valid survey designation (packed 
    or unpacked). It simply calls check_packed_unpacked() with the correct 
    compiled regular expressions in order to improve legibility and avoid 
    errors. See also is_valid_provisional_designation().

    *Input: asteroid designation (string or integer)

    *Return: boolean
    """

    try:
        designation = str(designation).strip()
        return is_packed_or_unpacked(designation, re_survey, re_packed_survey)
    except AttributeError:
        return False


def is_unpacked_survey_designation(designation: str) -> bool:
    try:
        designation = designation.strip()
        return designation_matches_compiled_re(designation, re_survey)
    except AttributeError:
        return False


def is_packed_survey_designation(designation: str) -> bool:
    try:
        designation: str = designation.strip()
        return designation_matches_compiled_re(designation, re_packed_survey)
    except AttributeError:
        return False


def is_valid_numbered_designation(designation: str) -> bool:
    """
    Check whether the input string or number is a valid numbered designation 
    (whether packed or unpacked), e.g. (1) Ceres, (1), 1, 00001, A1203, 101203,
    a1203, 361203, ~232s are all valid numbered designations. Unlike 
    is_valid_provisional_designation() or is_valid_survey_designation(), this does not simply 
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
    elif designation_matches_compiled_re(designation, re_packed_long):
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
    See also is_valid_survey_designation() and compare with is_valid_numbered_designation().

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


def is_an_asteroid_designation(designation):
    """
    This function checks whether the input is a valid asteroid designation. It 
    simply encapsulates calls to is_valid_provisional_designation(), 
    is_valid_survey_designation() and is_valid_numbered_designation().

    *Input: an asteroid designation (string or integer)

    *Return: boolean
    """

    if is_valid_provisional_designation(designation):
        return True
    elif is_valid_survey_designation(designation):
        return True
    elif is_valid_numbered_designation(designation):
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

    designation = str(designation).strip()

    found = compiled_re.findall(designation)
    if found and len(found) == 1:
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
    See also is_valid_numbered_designation() or is_valid_provisional_designation().

    *Input: designation is a string or an integer
    *Input: packed_compiled_re is a compiled regular expression conceived to find a
    certain type of packed designation, e.g. re_numbered_designation or reProv
    *Input: unpacked_compiled_re is a compiled regular expression conceived to find a
    certain type of unpacked designation, e.g. re_packed_numbered_designation or reProvPacked

    *Return: boolean
    """

    return designation_matches_compiled_re(designation, packed_compiled_re) or designation_matches_compiled_re(
        designation, unpacked_compiled_re)


def is_single_unpacked_provisional(designation: str) -> bool:
    """
    Check if the input both contains a match for a valid number designation
    and a provisional designation, e.g. "(341843) 2008 EV5". "2008 EV5" will 
    produce the same kind of match, so we must compare the matched number with
    the first part of the provisional designation. 

    *Input: an asteroid designation (string or int)

    *Return: boolean
    """
    is_single = False

    designation = str(designation).strip()
    if is_valid_provisional_designation(designation) and is_valid_numbered_designation(designation):

        found = re_provisional_designation.findall(designation)
        if found:
            first_part = found[0][0]
        else:
            return is_single
        found = re_numbered_designation.findall(designation)
        if found:
            num = found[0]
        else:
            return is_single

        if num == first_part:
            is_single = True

    return is_single


def pack_base_62(designation: Union[str, int]) -> str:
    """
    Pack a numbered designation greater than 619999 following the Minor 
    Planet Center's description.

    *Input: a valid numbered designation (string or integer)
    *Return: a string with the corresponding packed designation or an error 
    message
    """

    try:
        number = int(designation) - 620000
        result = ""
    except ValueError:
        return f"pack_base_62(): Error. {designation} is not a valid numbered designation"

    for i in range(4):
        q = number // 62
        rem = number % 62
        if rem > 9:
            rem = "{0}".format(unp2p_num[str(rem)])
        number = q
        result = str(rem) + result
    return "~" + "{0}".format(result)


def unpack_base_62(designation: Union[str, int]) -> str:
    """
    Unpack a numbered designation greater than 619999 (e.g. "~12z3") following 
    the Minor Planet Center's specification. 

    *Input: a valid packed numbered designation (string or integer)

    *Return: string with the corresponding unpacked designation or an error 
    message
    """
    error_message = "Error. {0} is not a valid packed long numbered designation".format(
        designation)

    if not (designation_matches_compiled_re(designation, re_packed_long)):
        return "unpack_base_62(): {0}".format(error_message)

    suma = 0
    designation = str(designation).strip()
    for i in range(4):
        pos_i = designation[1 + i]
        if pos_i.isdigit():
            num = int(pos_i)
        else:
            num = int(p2unp_num[designation[1 + i]])
        suma += num * np.power(62, 3 - i)
    return str(suma + 620000)


def pack_numbered_designation(designation: Union[str, int]) -> str:
    """
    Pack an input numbered asteroid designation, e.g. (1) Ceres, or 1 Ceres. If
    the input is already a valid numbered designation it returns it back. 

    *Input: a valid asteroid number designation (string or a number)

    *Return: string with the MPC-packed designation or an error message
    """

    error_message = f"pack_numbered_designation() error: '{designation}' not valid for packing"

    designation = str(designation).strip()
    if is_valid_numbered_designation(designation):
        try:
            # We remove parentheses
            number = int(re.sub("[\(\)]", "", designation.split(" ")[0]))
            if number > 619999:
                # We pack it with the base 62 notation
                return pack_base_62(number)
            elif number > 99999:
                # regex for the two groups to pack the first two digits:
                found = re6digits.findall(designation)
                pref = unp2p_num[found[0][0]]
                return pref + found[0][1]
            else:
                # it requires padding
                return "{0:05d}".format(number)

        except ValueError:
            # the int() failed, so it should be a valid packed designation
            return designation
    else:
        return error_message


def unpack_num(designation: Union[str, int]) -> str:
    """
    Return the unpacked version of the input number designation if it is
    a valid packed one, or the very input if it is a valid unpacked one.
    It returns an error message otherwise.

    *Input: asteroid designation (string or int)

    *Return: unpacked designation or error message
    """

    error_message = f"unpack_num(): Error. '{designation}' is not valid for unpacking"

    designation = str(designation).strip()
    if is_valid_numbered_designation(designation):
        found = re_packed_long.findall(designation)
        if found and len(found) == 1:
            return unpack_base_62(designation)
        else:
            found = re_packed_numbered_designation.findall(designation)
            if found and len(found) == 1:
                first = p2unp_num[found[0][0]]
                return first + found[0][1]
            else:
                found = re_numbered_designation.findall(designation)
                return "{0:d}".format(int(found[0]))
    else:
        return error_message


def pack_provisional_designation(designation: Union[str, int]) -> str:
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

    error_message = f"pack_provisional_designation(): Error. '{designation}' is not valid for packing"

    designation = str(designation).strip()
    if is_valid_provisional_designation(designation):

        found = re_provisional_designation.findall(designation)
        if found and len(found) == 1:
            # It must have worked:
            # so found must be of the form:
            # [('1923', '-', 'AG', '342')]
            #
            # year 1923 -> frst=19, scnd=23
            first = unp2p_prov[found[0][0][0:2]]
            second = found[0][0][2:]

            # half-month period, e.g. ABnumb -> ApackedB
            first_hm = found[0][2][0]
            second_hm = found[0][2][1]

            number_part = found[0][3]
            if len(number_part) == 0:
                middle_part = "00"
            elif len(number_part) > 2:
                # We pack the two first numbers
                middle_part = unp2p_num[number_part[0:2]] + number_part[2]
            else:
                middle_part = "{0:02d}".format(int(number_part))

            return first + second + first_hm + middle_part + second_hm

        else:
            # It might be already packed:
            found = re_packed_provisional_designation.findall(designation)
            if found and len(found) == 1:
                return designation
            else:
                return error_message
    else:
        return error_message


def unpack_provisional(designation: Union[str, int], separator: str):
    """Return the unpacked version of the input provisional designation if 
    it is a valid packed one, or the very input if it is a valid unpacked one.
    
    *Input: an asteroid designation (string or integer)
    *Input: a character that will be used as separator in the output provisional
    designation

    *Return: unpacked provisional designation (str) or an error message
    """

    error_message = f"unpack_provisional(): Error. '{designation}' not valid for unpacking"

    designation = re.sub("[ _]", "-", str(designation).strip(), count=1)
    if is_valid_provisional_designation(designation):
        found = re_provisional_designation.findall(designation)
        if found and len(found) == 1:
            # it is a valid provisional designation, already unpacked, so
            # we just insert the input separator
            return found[0][0] + separator + found[0][2] + found[0][3]

        found = re_packed_provisional_designation.findall(designation)
        year_part_1 = p2unp_prov[found[0][0]]
        year_part_2 = found[0][1]
        frst_fn = found[0][2]
        scnd_fn = found[0][5]
        try:
            n1 = int(found[0][3])
            if n1 < 1:
                n1 = ""
            else:
                n1 = str(n1)
        except ValueError:
            n1 = p2unp_num[found[0][3][0]]

        n2 = found[0][4]
        if int(found[0][4]) < 1:
            n2 = ""

        return year_part_1 + year_part_2 + separator + frst_fn + scnd_fn + n1 + n2
    else:
        return error_message


def pack_survey_desig(input_desig):
    """
    Pack a special survey asteroid designation.

    *Input: an asteroid designation

    *Return: a string with the packed designation or an error message
    """

    error_message = "{0} is not a valid special survey designation".format(input_desig)

    des = to_stripped_string(input_desig)

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

    des = to_stripped_string(input_desig)

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

    input_d = to_stripped_string(input_desig)

    single_provis = is_single_unpacked_provisional(input_d)

    if is_valid_survey_designation(input_d):
        if is_unpacked_survey_designation(input_d):
            return input_d
        else:
            return unpack_survey_desig(input_d)
    elif is_valid_numbered_designation(input_d) and not single_provis:
        return unpack_num(input_d)
    elif is_valid_provisional_designation(input_d):
        return unpack_provisional(input_d, str(separator))

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

    input_d = to_stripped_string(input_desig)

    single_provis = is_single_unpacked_provisional(input_d)

    if is_valid_survey_designation(input_d):
        return pack_survey_desig(input_d)
    elif is_valid_numbered_designation(input_d) and not (single_provis):
        return pack_numbered_designation(input_d)
    elif is_valid_provisional_designation(input_d):
        return pack_provisional_designation(input_d)
    else:
        return error_message


def convert(input_, p_or_unp):
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

    input_ = str(input_)
    if len(input_) > 0 and is_an_asteroid_designation(input_):
        designations = [input_]
        # Create a list with the input so that we can iterate over it
    else:
        try:
            # Perhaps it is an input filename, not a designation
            my_file = open(input_, 'r')
            designations = my_file.readlines()
            my_file.close()
        except IOError:
            print("convert(): Error. Did not find file '{0}'".format(input_))
            designations = []
            # We still need an empty list to iterate over

    for designation in designations:
        if len(designation.split()) < 1:
            print("convert(): Warning. Input is an empty line")
        elif "unpack" in p_or_unp:
            print(unpack(designation.replace("\n", ""), "_"))
        elif len(p_or_unp) == 4 and "pack" in p_or_unp:
            print(pack(designation.replace("\n", "")))
        else:
            print("convert(): Error. 2nd arg. must be 'pack' or 'unpack'")


def main():
    parsed = argParserMPC.parse_args()

    if not (parsed.pack or parsed.unpack):
        print("main(): Error. Either -p or -u must be used")
        sys.exit(-1)

    if parsed.designation:
        # if we parsed a designation, we have a list with one element
        designations = [parsed.designation]

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
