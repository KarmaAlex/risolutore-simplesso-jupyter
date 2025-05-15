import re
from typing import Optional
from enum import Enum
from math import gcd, lcm

#Pattern to match variables with their associated multipliers
var_pattern:re.Pattern = re.compile("(?:[+]?(-?[^x]*)x_([^-+=]*))")

def parse_variables_of(f:str):
    "Parse variables and their multipliers from objective function"
    variables:list[tuple[int,str | int]] = []

    #Find instances of the pattern, moving forward in the string for each one found
    find:Optional[re.Match[str]] = var_pattern.search(f)
    while (find is not None):
        t:str = str(find.groups(0)[0])
        #If multiplier is missing set it as + or -1
        if t =='': t = "1"
        elif t == '-': t = "-1"
        variables.append((int(find.groups()[1]), t))
        find = var_pattern.search(f, pos=find.end())

    #Length of the first row is based on the highest index found
    max:int = 0
    for i in variables: 
        if i[0] > max: max = i[0]
    out:list[str] = [''] * max
    #Copy the multiplier of each variable to its corresponding position in the row
    for i in variables:
        out[i[0]-1] = str(i[1])
    #Fill empty spaces with zero
    for i in range(len(out)):
        if out[i] is None: out[i] = "0"
    return out


def parse_variables_st(s:list[str]):
    "Parse variables and their multipliers from limiting equations"
    variables:list[list[tuple[int,str]]] = []
    #Pattern to match known value, so everything to the right of the = sign
    kv_pattern:re.Pattern = re.compile(".*=(?P<kv>.*?)$")
    #Search for all variables and their multipliers
    for i in s:
        temp:list[tuple[int, str]] = []
        find:Optional[re.Match[str]] = var_pattern.search(i)
        while (find is not None):
            t:str = str(find.groups()[0])
            #If multiplier is missing set it as + or -1
            if t=='': t = "1"
            elif t=='-': t ="-1"
            temp.append((int(find.groups()[1]), t))
            find = var_pattern.search(i, pos=find.end())
        variables.append(temp)
    #Max size of a row is determined by the highest variable index found
    max:int = 0
    for i in variables:
        for j in i:
            if j[0] > max: max = j[0]
    out:list[list[str]] = [['' for _ in range(max+1)] for _ in range(len(s))]
    #Add known values at the end of each row
    for i in range(len(out)):
        t2:re.Match[str] | None = kv_pattern.match(s[i])
        if (t2 is not None): out[i][max] = t2.group("kv")
    #Copy values to matrix
    for i in range(len(variables)):
        for j in range(len(variables[i])):
            out[i][variables[i][j][0]-1] = variables[i][j][1]
    #Fill empty spaces with zero
    for i in range(len(out)):
        for j in range(len(out[i])):
            if out[i][j] == '': out[i][j] = "0"
    return out


def build_tableau(first_row:list[str], other_rows:list[list[str]]):
    "Builds the tableau from the first row (taken from the objective function) and a matrix of the other rows (taken from the limiting equations)"
    lf:int = len(first_row)
    lo:int = len(other_rows[0]) - 1
    #If one is smaller than the other extend one to match the other
    if lf > lo:
        first_row.append("0")
        for i in range(len(other_rows)):
            for _ in range(lo, lf):
                other_rows[i].append("0")
            other_rows[i][-1] = other_rows[i][lo]
            other_rows[i][lo] = "0"
    else:
        for _ in range(lf, lo+1): first_row.append("0")

    tableau:list[list[str]] = []
    tableau.append(first_row)
    row: list[str]
    for row in other_rows: tableau.append(row)

    return tableau


def output_tableau(t:list[list[str]]):
    "Returns tableau as a printable HTML element with Latex notation, to be used as display(Latex(output_tableau(tableau)))"
    out:str = "<table>"
    for i in t:
        out += "<tr>"
        for j in i:
            out += "<td>\n\n$" + j.replace("'",'').replace("\\\\",'\\') + "$\n</td>\n"
        out += "</tr>"
    out += "</table>"
    
    return out


def find_id(t:list[list[str]]):
    #Finds identity matrix or columns that would be part of one
    cols:list[tuple[int, int]] = []
    for i in range(len(t[0])-1):
        if t[0][i] == "0":
            j:int = 1
            id_col:bool = True
            loc_one:tuple[int, int] | None = None
            while (j<len(t) and id_col):
                if (not (t[j][i] == "1" or t[j][i] == "0")): 
                    id_col = False
                    break
                #When we find a candidate we save the coordinates of the 1 as a tuple
                elif (t[j][i] == "1" and loc_one is None): loc_one = (j,i)
                elif (t[j][i] == "1" and loc_one is not None): id_col = False
                j += 1
            #Once we know that the 1 we found is a valid candidate we check if we have already found one in the same vertical position
            if(id_col and loc_one is not None):
                dup = False
                for c in cols:
                    if c[0] == loc_one[0]: 
                        dup = True
                        break
                if not dup : cols.append(loc_one)
    return cols

#Pattern that extracts numbers from the latex format \\frac{x}{y}
num_extract_pattern = re.compile(".*\\{([0-9]*)\\}\\s?\\{([1-9]*)\\}$")
def extract_nums(string:str):
    "Extract numbers from a Latex formatted fraction string"
    n:int; d:int

    match:Optional[re.Match[str]] = num_extract_pattern.match(string)
    if match is not None:
        n = int(match.groups()[0])
        d = int(match.groups()[1])
        if string[:1] == "-" : n = -n
        return n, d
    return 0, 0


def simplify(n, d):
    "Divide two values by their greatest common denominator"
    p = gcd(n, d)
    return int(n/p), int(d/p)

#Used as an argument of rational_op to specify operation type
operations = Enum("Operations", [("ADD", 1), ("MULT", 2), ("DIV", 3)])


def rational_op(num1:str, num2:str, op_type:operations):
    "Operations between rational numbers"
    res:str = "1"
    n1: int; n2:int; d1:int; d2:int
    #If there is a backslash in the string that means it's a fraction
    if ("\\" in num1): n1, d1 = extract_nums(num1)
    #If it's not a fraction we still treat it as one with a denominator of 1
    else: n1 = int(num1); d1 = 1
    if ("\\" in num2): n2, d2 = extract_nums(num2)
    else: n2 = int(num2); d2 = 1        
    match op_type:
        case operations.ADD:
            n1 += n2*lcm(d1, d2)
            d1 = lcm(d1, d2)
        case operations.MULT:
            n1*=n2
            d1*=d2
        case operations.DIV:
            n1*=d2
            d1*=n2
    n1, d1 = simplify(n1, d1)
    #Output result as a formatted string if it is a fraction or as the number itself
    res = r"\\frac{" + repr(abs(n1)) + r"}{" + repr(d1) + r"}" if d1 != 1 else repr(abs(n1))
    #Make negative if answer is < 0
    if n1 < 0: res = "-" + res[0:]

    return res


def solve_artificial(t:list[list[str]], inBase:list[tuple[int, int]]):
    "Solve the associated aritificial problem and return a valid base"
    res:list[tuple[int,int]] = []
    copy:list[list[str]] = list(t)
    res = list(inBase)

    for i in range(len(inBase), len(t)-1):
        for j in range(len(copy)):
            copy[j].append(copy[j][-1])
            copy[j][-2] = "0"

    j:int = 0
    for i in range(1, len(copy)):
        dup:bool = False
        for t3 in res:
            if i == t3[0]:
                dup = True
                break
        if not dup:
            res.append((i, len(t)-1+j))
            copy[res[-1][0]][res[-1][1]] = "1"
            copy[0][res[-1][1]]="1"
            j+=1
    
    for i in range(1, len(t[0])):
        for j in range(len(t)):
            copy[0][j] = rational_op(copy[0][j], copy[i][j], operations.ADD)
        
    return res


def find_base(t:list[list[str]]):
    "Find a valid base for the given tableau"
    base:list[tuple[int, int]] = []
    #First off check if any of the pre-existing variables are part of a valid base
    id_cols = find_id(t)
    if (len(id_cols) == len(t)-1): base = id_cols
    #If there aren't enough then solve the associated artificial problem to find the rest
    else: base = solve_artificial(t, id_cols)
    return base