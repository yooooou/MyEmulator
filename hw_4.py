# coding: utf-8
# python 2.7
import re
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt

filename = raw_input("please enter netlist filename:")
file_handle = open(filename, 'r')

element_list = []
v_list = []
l_list = []
c_list = []
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


def ac_analysis(points, step, ac_res_list, omega_list, start, type):
    for i in range(points):
        MNA_ac = np.zeros((rows, rows), complex)
        if type == "lin":
            freq = start + i * step
        elif type == "dec":
            freq = 10 ** (start + i * step)
        else:
            freq = 2 ** (start + i * step)
        omega = freq * 2 * math.pi
        for c_element in c_list:
            n1 = c_element[1] - 1
            n2 = c_element[2] - 1
            sc = complex(0, omega * c_element[3])
            MNA_ac[n1][n1] += sc
            if n2 >= 0:
                MNA_ac[n1, n2] += -sc
                MNA_ac[n2, n1] += -sc
                MNA_ac[n2, n2] += sc

        for l_element in l_list:
            n1 = l_element[1] - 1
            n2 = l_element[2] - 1
            sl = complex(0, omega * l_element[3])
            br_l = l_element[-1] + col_normal
            MNA_ac[br_l - 1, br_l - 1] += -sl
        MNA_ac += MNA_dc
        print ("omega = %f rad/s" % omega)
        print "MNA_ac:", MNA_ac
        ac_res = np.linalg.solve(MNA_ac, RHS_ac)

        print "ac results:", ac_res
        ac_res_list.append(ac_res)
        omega_list.append(omega)


while line != ".end":
    line_elements = re.split(r'[=\s]+', line)  # extract line elements separated by spaces and "="
    if line[0] == "*":
        print "comment line:", line
    # elif line[0] in ["r","c","l","d","m","v","i","e","f","g","h","s"]:
    elif line[0] in ["r", "c", "v", "l", "i"]:
        if "dc" in line_elements:
            line_elements.remove("dc")
        for i in range(1, 3):
            line_elements[i] = int(line_elements[i])
            if line_elements[i] > col_normal:
                col_normal = line_elements[i]
        line_elements[3] = str2num(line_elements[3])
        if line[0] != "v":
            if line[0] == "l":
                branch += 1
                line_elements.append(branch)  # save branch info
                l_list += [line_elements]
            elif line[0] == "c":
                c_list += [line_elements]
            else:
                element_list += [line_elements]  # save elements
        else:
            if "ac" in line_elements:
                line_elements.remove("ac")
                line_elements[4] = str2num(line_elements[4])
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
            if line_elements[0] == "ac":
                for i in range(2, 5):
                    line_elements[i] = str2num(line_elements[i])
            control_list += [line_elements]  # save control
        else:
            model_list += [line_elements]  # save model

    line = file_handle.readline().strip().lower()
    if not line:
        break
print "******************************parser***************************************"
print "element_list:", element_list
print "v_list:", v_list
print "c_list:", c_list
print "l_list:", l_list
print "control_list:", control_list
print "model_list:", model_list
print "col_normal:", col_normal
print "branch:", branch
print "****************************dc analysis***************************************"
rows = col_normal + branch
MNA_dc = np.zeros((rows, rows))
RHS_dc = [0] * rows
RHS_ac = [0] * rows
RHS_i = [0] * rows

for vs in v_list:
    n1 = vs[1] - 1
    n2 = vs[2] - 1
    br = vs[-1] + col_normal
    RHS_dc[br - 1] = vs[3]
    if len(vs) >= 6:
        RHS_ac[br - 1] = vs[4]
    MNA_dc[n1, br - 1] += 1
    MNA_dc[br - 1, n1] += 1
    if n2 >= 0:
        MNA_dc[n2, br - 1] += -1
        MNA_dc[br - 1, n2] += -1

# dc stamp
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
            RHS_i[n2] += element[3]
        else:
            RHS_i[n1] += -element[3]
            if n2 >= 0:
                RHS_i[n2] += element[3]

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

for l_element in l_list:
    n1 = l_element[1] - 1
    n2 = l_element[2] - 1
    br_l = l_element[-1] + col_normal
    MNA_dc[n1, br_l - 1] += 1
    MNA_dc[br_l - 1, n1] += 1
    if n2 >= 0:
        MNA_dc[n2, br_l - 1] += -1
        MNA_dc[br_l - 1, n2] += -1

RHS_dc = map(lambda (a, b): a + b, zip(RHS_dc, RHS_i))
RHS_ac = map(lambda (a, b): a + b, zip(RHS_ac, RHS_i))
print "MNA_dc:", MNA_dc
print "RHS_dc:", RHS_dc
try:
    dc_res = np.linalg.solve(MNA_dc, RHS_dc)
    print "dc results:", dc_res
except:
    print "no dc solution"

for control_command in control_list:
    if "ac" in control_command:
        ac_res_list = []
        omega_list = []
        start = control_command[3]
        end = control_command[4]
        print "****************************ac analysis***************************************"
        print "RHS_ac:", RHS_ac
        if control_command[1] == "lin":
            step = (end - start) / (control_command[2] + 1.0)
            ac_analysis(control_command[2] + 2, step, ac_res_list, omega_list, start, "lin")

        elif control_command[1] == "dec":
            dec_start = math.log10(start)
            dec_end = math.log10(end)
            dec_step = 1 / (control_command[2] + 1.0)
            dec_points = (dec_end - dec_start) * (control_command[2] + 1) + 1
            ac_analysis(int(dec_points), dec_step, ac_res_list, omega_list, dec_start, "dec")
        else:
            oct_start = math.log(start, 2)
            oct_end = math.log(end, 2)
            oct_step = 1 / (control_command[2] + 1.0)
            oct_points = (oct_end - oct_start) * (control_command[2] + 1) + 1
            ac_analysis(int(oct_points), oct_step, ac_res_list, omega_list, oct_start, "oct")
        plot_amplitude = []
        plot_phase = []
        f_list = []
        for v12 in ac_res_list:
            v_1_2 = v12[0] - v12[1]
            # amplitude = 20*math.log10(abs(v_1_2))
            amplitude = abs(v_1_2)
            # print amplitude
            phase = 180 * math.atan2(v_1_2.imag, v_1_2.real) / math.pi
            plot_amplitude.append(amplitude)
            plot_phase.append(phase)
        for omega in omega_list:
            f_list.append(math.log10(omega / (2 * math.pi)))
        plt.subplot(2, 1, 1)
        plt.plot(f_list, plot_amplitude)
        plt.subplot(2, 1, 2)
        plt.plot(f_list, plot_phase)
        plt.show()
