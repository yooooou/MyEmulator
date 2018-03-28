# coding: utf-8
# python 2.7
import re
import math
import numpy as np

filename = raw_input("please enter netlist filename:")
file_handle = open(filename, 'r')

element_list = []
v_list = []
control_list = []
model_list = []
line = file_handle.readline().strip().lower()
col_normal = 0
branch = 0


def str2num(str):
    if "." not in str:  # int 
        try:
            num = int(str)
        except ValueError:
            if 'db' in str:
                num = 20 * math.log10(int(str[0:len(str) - 2]))
            elif 'meg' in str:
                num = int(str[0:len(str) - 3]) * 1e6
            else:
                num = int(str[0:len(str) - 1])
                sign = str[len(str) - 1]
                if sign == 'k':
                    num *= 1e3
                elif sign == 'g':
                    num *= 1e9
                elif sign == 't':
                    num *= 1e12
                elif sign == 'f':
                    num *= 1e-15
                elif sign == 'p':
                    num *= 1e-12
                elif sign == 'n':
                    num *= 1e-9
                elif sign == 'u':
                    num *= 1e-6
                elif sign == 'm':
                    num *= 1e-3
    else:  # float
        try:
            num = float(str)
        except ValueError:
            if 'db' in str:
                num = 20 * math.log10(float(str[0:len(str) - 2]))
            elif 'meg' in str:
                num = float(str[0:len(str) - 3]) * 1e6
            else:
                num = float(str[0:len(str) - 1])
                sign = str[len(str) - 1]
                if sign == 'k':
                    num *= 1e3
                elif sign == 'g':
                    num *= 1e9
                elif sign == 't':
                    num *= 1e12
                elif sign == 'f':
                    num *= 1e-15
                elif sign == 'p':
                    num *= 1e-12
                elif sign == 'n':
                    num *= 1e-9
                elif sign == 'u':
                    num *= 1e-6
                elif sign == 'm':
                    num *= 1e-3
    return num


while line != ".end":
    line_elements = re.split(r'[=\s]+', line)  # extract line elements separated by spaces and "="
    if line[0] == "*":
        print "comment line:", line
    # elif line[0] in ["r","c","l","d","m","v","i","e","f","g","h","s"]:
    elif line[0] in ["r", "c", "v", "l", "i"]:
        for i in range(1, 3):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]
        line_elements[3] = str2num(line_elements[3])
        if line[0] != "v":
            if line[0] == "l":
                branch += 1
                line_elements.append(branch)  # save branch info
            element_list += [line_elements]  # save elements
        else:
            branch += 1
            line_elements.append(branch)
            v_list += [line_elements]

    elif line[0] in ["e", "g"]:
        for i in range(1, 5):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]
        line_elements[5] = str2num(line_elements[5])
        if line[0] == "e":
            branch += 1
            line_elements.append(branch)  # save branch info
        element_list += [line_elements]

    elif line[0] in ["f", "h"]:
        for i in range(1, 3):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]
        line_elements[4] = str2num(line_elements[4])
        if line[0] == "h":
            branch += 1
            line_elements.append(branch)  # save branch info
        element_list += [line_elements]

    elif line[0] == ".":
        line_elements[0] = line_elements[0].replace(".", "")
        if line_elements[0] != "model":
            control_list += [line_elements]  # save control
        else:
            model_list += [line_elements]  # save model

    line = file_handle.readline().strip().lower()
    if not line:
        break

print "element_list:", element_list
print "v_list:", v_list
print "control_list:", control_list
print "model_list:", model_list
print col_normal
print branch

rows = col_normal + branch
MNA_dc = np.zeros((rows, rows))
MNA_ac = np.zeros((rows, rows), complex)
RHS = [0] * rows
# k = len(element_list) - branch
for vs in v_list:
    n1 = vs[1] - 1
    n2 = vs[2] - 1
    br = vs[-1] + col_normal
    RHS[br - 1] = vs[3]
    MNA_dc[n1, br - 1] += 1
    MNA_dc[br - 1, n1] += 1
    if n2 >= 0:
        MNA_dc[n2, br - 1] += -1
        MNA_dc[br - 1, n2] += -1

for element in element_list:
    n1 = element[1] - 1
    n2 = element[2] - 1

    if element[0][0] == "r":
        g = 1.0 / element[3]
        MNA_dc[n1, n1] += g
        if n2 >= 0:
            MNA_dc[n1, n2] += -g
            MNA_dc[n2, n1] += -g
            MNA_dc[n2, n2] += g

    elif element[0][0] == "i":
        if n1 < 0:
            RHS[n2] += element[3]
        else:
            RHS[n1] += -element[3]
            if n2 >= 0:
                RHS[n2] += element[3]

    elif element[0][0] == "e":
        br = element[-1] + col_normal
        n3 = element[3] - 1
        n4 = element[4] - 1
        MNA_dc[n1, br - 1] += 1
        MNA_dc[br - 1, n1] += 1
        MNA_dc[br - 1, n3] += -element[5]
        if n2 >= 0:
            MNA_dc[n2, br - 1] += -1
            MNA_dc[br - 1, n2] += -1
        if n4 >= 0:
            MNA_dc[br - 1, n4] += element[5]

    elif element[0][0] == "f":
        for v_comp in v_list:
            if v_comp[0] == element[3]:
                br = v_comp[-1] + col_normal
                if n1 >= 0:
                    MNA_dc[n1, br - 1] += element[4]
                if n2 >= 0:
                    MNA_dc[n2, br - 1] += -element[4]
                break

    elif element[0][0] == "g":
        n3 = element[3] - 1
        n4 = element[4] - 1
        if n1 >= 0:
            MNA_dc[n1, n3] += element[5]
            if n4 >= 0:
                MNA_dc[n1, n4] += -element[5]
        if n2 >= 0:
            MNA_dc[n2, n3] += -element[5]
            if n4 >= 0:
                MNA_dc[n1, n4] += element[5]

    elif element[0][0] == "h":
        br_vs = element[-1] + col_normal
        MNA_dc[n1, br_vs - 1] += 1
        MNA_dc[br_vs - 1, n1] += 1
        if n2 >= 0:
            MNA_dc[n2, br_vs - 1] += -1
            MNA_dc[br_vs - 1, n2] += -1
        for v_comp in v_list:
            if v_comp[0] == element[3]:
                br = v_comp[-1] + col_normal
                MNA_dc[br_vs - 1, br - 1] = -element[4]
            break

    elif element[0][0] == "c":
        sc = complex(0, element[3])
        MNA_ac[n1][n1] += sc
        if n2 >= 0:
            MNA_ac[n1, n2] += -sc
            MNA_ac[n2, n1] += -sc
            MNA_ac[n2, n2] += sc
    elif element[0][0] == "l":
        sl = complex(0, element[3])
        br_l = element[-1] + col_normal
        MNA_ac[n1, br_l - 1] += 1
        MNA_ac[br_l - 1, n1] += 1
        MNA_ac[br_l - 1, br_l - 1] += -sl
        if n2 >= 0:
            MNA_ac[n2, br_l - 1] += -1
            MNA_ac[br_l - 1, n2] += -1
MNA = MNA_dc + MNA_ac
print MNA_dc
print MNA_ac
print MNA
print RHS
x = np.linalg.solve(MNA_dc, RHS)
print x