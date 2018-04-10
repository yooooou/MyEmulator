# coding: utf-8
# python 2.7

import myparser
import myengine
import math
import numpy as np
import matplotlib.pyplot as plt

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
col_br_list = [0, 0, 0]
while line != ".end":
    myparser.line_parser(line, col_br_list, l_list, c_list, element_list, v_list, i_list, d_list, control_list, model_list)
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
print "d_list:", d_list
print "control_list:", control_list
print "model_list:", model_list
print "col_normal:", col_normal
print "branch:", branch
print "branch_c:", branch_c
print "****************************dc analysis***************************************"
rows = col_normal + branch
MNA_dc = np.zeros((rows, rows))
RHS_dc = [0] * rows
RHS_ac = [0] * rows
dc_res = myengine.dc_stamp(col_normal, MNA_dc, RHS_dc, RHS_ac, v_list, i_list, d_list, element_list, l_list, rows)

for control_command in control_list:
    if "ac" in control_command:
        ac_res_list = []
        omega_list = []
        print "****************************ac analysis***************************************"
        print "RHS_ac:", RHS_ac
        myengine.ac_analysis(control_command, rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, ac_res_list, omega_list)
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

    if "tran" in control_command:
        tran_rows = rows + branch_c
        tran_res_list = []
        tran_print_list = []
        tran_res_t0 = list(dc_res) + [0] * branch_c
        # print tran_res_t0
        tran_res_list.append(tran_res_t0)
        MNA_tran_cols = np.zeros((rows, branch_c))  # branch_c zero cols
        MNA_tran_rows = np.zeros((branch_c, tran_rows))  # branch_c zero rows
        MNA_tran = np.vstack((np.hstack((MNA_dc, MNA_tran_cols)), MNA_tran_rows))
        time_list = []
        print "****************************tran analysis***************************************"
        myengine.tran_analysis(control_command, MNA_tran, tran_res_list, tran_print_list, c_list, l_list,
                               v_list, i_list, d_list, time_list, rows, col_normal, tran_rows)
        plot_voltage = []
        for v2 in tran_print_list:
            plot_voltage.append(v2[1])
        plt.plot(time_list, plot_voltage)
        plt.show()
