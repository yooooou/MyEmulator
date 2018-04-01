# coding: utf-8
# python 2.7

import re
import math


def str2num(str):
    str = re.sub(r'[vas]','',str)  # remove "V" "A" "S"
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

def line_parser(line, col_br_list, l_list, c_list, element_list, v_list, i_list, control_list, model_list):
    col_normal= col_br_list[0]
    branch = col_br_list[1]
    branch_c = col_br_list[2]
    line_elements = re.split(r'[=\s()]+', line)  # extract line elements separated by spaces "=" "(" ")"
    if line[0] == "*":
        print "comment line:", line
    # elif line[0] in ["r","c","l","d","m","v","i","e","f","g","h","s"]:
    elif line[0] in ["r", "c", "v", "l", "i"]:

        for i in range(1, 3):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]

        if line[0] == "v":
            branch += 1
            v_dict = {"name":line_elements[0],"node+":line_elements[1],"node-":line_elements[2],"dc_value":0,
                      "ac_mag":0,"ac_phase":0,"tran_mag":0,"tran_freq":0,"branch_info":branch}
            if "dc" in line_elements:
                line_elements.remove("dc")
                v_dict['dc_value'] = str2num(line_elements[3])
            if "ac" in line_elements:
                index_ac = line_elements.index("ac")
                v_dict['ac_mag'] = str2num(line_elements[index_ac+1])
            if "sin" in line_elements:
                index_sin = line_elements.index("sin")
                v_dict["dc_value"] = str2num(line_elements[index_sin+1])
                v_dict["tran_mag"] = str2num(line_elements[index_sin+2])
                v_dict["tran_freq"] = str2num(line_elements[index_sin+3])
            v_list.append(v_dict)

        elif line[0] == "i":
            i_dict = {"name":line_elements[0],"node+":line_elements[1],"node-":line_elements[2],"dc_value":0,
                      "ac_mag":0,"ac_phase":0,"tran_mag":0,"tran_freq":0}
            if "dc" in line_elements:
                line_elements.remove("dc")
                i_dict['dc_value'] = str2num(line_elements[3])
            if "ac" in line_elements:
                index_ac = line_elements.index("ac")
                i_dict['ac_mag'] = str2num(line_elements[index_ac+1])
            if "sin" in line_elements:
                index_sin = line_elements.index("sin")
                i_dict["dc_value"] = str2num(line_elements[index_sin+1])
                i_dict["tran_mag"] = str2num(line_elements[index_sin+2])
                i_dict["tran_freq"] = str2num(line_elements[index_sin+3])
            i_list.append(i_dict)
        else:
            line_elements[3] = str2num(line_elements[3])
            if line[0] == "l":
                branch += 1
                line_elements.append(branch)  # save branch info
                l_list += [line_elements]
            elif line[0] == "c":
                branch_c += 1
                line_elements.append(branch_c)  # save branch info for tran
                c_list += [line_elements]
            else:
                element_list += [line_elements]  # save elements

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
            if line_elements[0] == "ac":
                for i in range(2, 5):
                    line_elements[i] = str2num(line_elements[i])
            if line_elements[0] == "tran":
                for i in range(1,len(line_elements)):
                    line_elements[i] = str2num(line_elements[i])
            control_list += [line_elements]  # save control
        else:
            model_list += [line_elements]  # save model
    col_br_list[0] = col_normal
    col_br_list[1] = branch
    col_br_list[2] = branch_c

if __name__ == '__main__':
    filename = raw_input("please enter netlist filename:")
    file_handle = open(filename, 'r')
    element_list = []
    v_list = []
    i_list = []
    l_list = []
    c_list = []
    control_list = []
    model_list = []
    line = file_handle.readline().strip().lower()
    col_br_list = [0,0]
    while line != ".end":
        line_parser(line, col_br_list, l_list, c_list, element_list, v_list, control_list, model_list)
        line = file_handle.readline().strip().lower()
        if not line:
            break
    col_normal = col_br_list[0]
    branch = col_br_list[1]
    print "******************************parser***************************************"
    print "element_list:", element_list
    print "v_list:", v_list
    print "i_list:", i_list
    print "c_list:", c_list
    print "l_list:", l_list
    print "control_list:", control_list
    print "model_list:", model_list
    print "col_normal:", col_normal
    print "branch:", branch
