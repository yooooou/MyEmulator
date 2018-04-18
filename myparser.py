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

def line_parser(line, col_br_list, l_list, c_list, element_list, v_list, i_list, d_list, mos_list,
                control_list, model_list):
    col_normal= col_br_list[0]
    branch = col_br_list[1]
    branch_c = col_br_list[2]
    line_elements = re.split(r'[=\s(),]+', line)  # extract line elements separated by spaces "=" "(" ")"
    if line[0] == "*":
        print "comment line:", line
    # elif line[0] in ["r","c","l","d","m","v","i","e","f","g","h","s"]:
    elif line[0] in ["r", "c", "v", "l", "i", "d", "m"]:

        for i in range(1, 3):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]

        if line[0] == "v":
            branch += 1
            v_dict = {"name":line_elements[0],"node+":line_elements[1],"node-":line_elements[2],"dc_value":0,
                      "tran_type":"non", "ac_mag":0,"ac_phase":0,"tran_mag":0,"tran_freq":0,"branch_info":branch,
                      "pulse_v1":0, "pulse_v2":0, "td":0, "tr":0, "tf":0, "pw":0, "per":0}
            if "dc" in line_elements:
                line_elements.remove("dc")
            if len(line_elements) > 3:
                try:v_dict['dc_value'] = str2num(line_elements[3])
                except ValueError: pass
                if "ac" in line_elements:
                    index_ac = line_elements.index("ac")
                    v_dict['ac_mag'] = str2num(line_elements[index_ac+1])
                if "sin" in line_elements:
                    index_sin = line_elements.index("sin")
                    v_dict["tran_type"] = "sin"
                    v_dict["dc_value"] = str2num(line_elements[index_sin+1])
                    v_dict["tran_mag"] = str2num(line_elements[index_sin+2])
                    v_dict["tran_freq"] = str2num(line_elements[index_sin+3])
                if "pulse" in line_elements:
                    index_pulse = line_elements.index("pulse")
                    v_dict["tran_type"] = "pulse"
                    v_dict["dc_value"] = str2num(line_elements[index_pulse+1])
                    v_dict["pulse_v1"] = v_dict["dc_value"]
                    v_dict["pulse_v2"] = str2num(line_elements[index_pulse+2])
                    v_dict["td"] = str2num(line_elements[index_pulse+3])
                    v_dict["tr"] = str2num(line_elements[index_pulse+4])
                    v_dict["tf"] = str2num(line_elements[index_pulse+5])
                    v_dict["pw"] = str2num(line_elements[index_pulse+6])
                    v_dict["per"] = str2num(line_elements[index_pulse+7])
            v_list.append(v_dict)

        elif line[0] == "i":
            i_dict = {"name":line_elements[0],"node+":line_elements[1],"node-":line_elements[2],"dc_value":0,
                      "tran_type":"non", "ac_mag":0,"ac_phase":0,"tran_mag":0,"tran_freq":0,"branch_info":branch,
                      "pulse_v1":0, "pulse_v2":0, "td":0, "tr":0, "tf":0, "pw":0, "per":0}
            if "dc" in line_elements:
                line_elements.remove("dc")
            if len(line_elements) > 3:
                try: i_dict['dc_value'] = str2num(line_elements[3])
                except ValueError: pass
                if "ac" in line_elements:
                    index_ac = line_elements.index("ac")
                    i_dict['ac_mag'] = str2num(line_elements[index_ac+1])
                if "sin" in line_elements:
                    index_sin = line_elements.index("sin")
                    i_dict["tran_type"] = "sin"
                    i_dict["dc_value"] = str2num(line_elements[index_sin + 1])
                    i_dict["tran_mag"] = str2num(line_elements[index_sin + 2])
                    i_dict["tran_freq"] = str2num(line_elements[index_sin + 3])
                if "pulse" in line_elements:
                    index_pulse = line_elements.index("pulse")
                    i_dict["tran_type"] = "pulse"
                    i_dict["pulse_v1"] = str2num(line_elements[index_pulse + 1])
                    i_dict["pulse_v2"] = str2num(line_elements[index_pulse + 2])
                    i_dict["td"] = str2num(line_elements[index_pulse + 3])
                    i_dict["tr"] = str2num(line_elements[index_pulse + 4])
                    i_dict["tf"] = str2num(line_elements[index_pulse + 5])
                    i_dict["pw"] = str2num(line_elements[index_pulse + 6])
                    i_dict["per"] = str2num(line_elements[index_pulse + 7])
            i_list.append(i_dict)

        elif line[0] == "d":
            d_list += [line_elements]

        elif line[0] == "m":
            for i in range(3, 5):
                line_elements[i] = int(line_elements[i])
                if line_elements[i] > col_normal:
                    col_normal = line_elements[i]

            mos_dict = {"name":line_elements[0], "drain":line_elements[1], "gate":line_elements[2],
                        "source":line_elements[3], "body": line_elements[4],
                        "model_name":line_elements[5], "length":1e-6, "width":1e-6}
            if "l" in line_elements:
                index_length = line_elements.index("l")
                mos_dict['length'] = str2num(line_elements[index_length + 1])
            if "w" in line_elements:
                index_width = line_elements.index("w")
                mos_dict['width'] = str2num(line_elements[index_width + 1])
            mos_list.append(mos_dict)

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
        if line_elements[0] != "model" :    #.dc .ac .tran
            for i in range(1,len(line_elements)):
                try:line_elements[i] = str2num(line_elements[i])
                except ValueError: pass
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
    d_list = []
    control_list = []
    model_list = []
    line = file_handle.readline().strip().lower()
    col_br_list = [0,0,0]
    while line != ".end":
        line_parser(line, col_br_list, l_list, c_list, element_list, v_list, i_list, d_list, control_list, model_list)
        line = file_handle.readline().strip().lower()
        if not line:
            break
    col_normal = col_br_list[0]
    branch = col_br_list[1]
    branch_c = col_br_list[2]
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
