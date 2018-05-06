# coding: utf-8
# python 2.7
from Tkconstants import END

import myparser
import myengine
import math
import numpy as np
import matplotlib.pyplot as plt


def engine(filename, text_output):
    file_handle = open(filename, 'r')
    element_list = []
    v_list = []
    i_list = []
    l_list = []
    c_list = []
    d_list = []
    mos_list = []
    control_list = []
    model_list = []
    line = file_handle.readline().strip().lower()
    col_br_list = [0, 0, 0]
    while line != ".end":
        myparser.line_parser(line, col_br_list, l_list, c_list, element_list, v_list, i_list, d_list, mos_list,
                             control_list, model_list)
        line = file_handle.readline().strip().lower()
        if not line:
            break
    file_handle.close()
    col_normal = col_br_list[0]
    branch = col_br_list[1]
    branch_c = col_br_list[2]
    # text_print = []
    text_output.insert(END,"****************************dc analysis***************************************\n")
    # print "******************************parser***************************************"
    # print "element_list:", element_list
    # print "v_list:", v_list
    # print "i_list:", i_list
    # print "c_list:", c_list
    # print "l_list:", l_list
    # print "d_list:", d_list
    # print "mos_list:", mos_list
    # print "control_list:", control_list
    # print "model_list:", model_list
    # print "col_normal:", col_normal
    # print "branch:", branch
    # print "branch_c:", branch_c
    # print "****************************dc analysis***************************************"

    rows = col_normal + branch
    MNA_dc = np.zeros((rows, rows))
    RHS_dc = [0] * rows
    RHS_ac = [0] * rows
    dc_res = myengine.dc_stamp(col_br_list, MNA_dc, RHS_dc, RHS_ac, v_list, i_list, d_list, mos_list,
                               element_list, l_list)
    text_output.insert(END,"result: ")
    text_output.insert(END,dc_res)

    dc_2srcs_sweep_list = []
    src2 = []
    ac_swepp_type = []
    ac_res_list = []
    freq_list = []
    dc_src1 = ''
    for control_command in control_list:
        if control_command[0] == 'dc':
            # print "****************************dc sweep******************************************"
            text_output.insert(END, "\n****************************dc sweep******************************************")
            dc_src1 = control_command[1]
            dc_sweep_list = []
            dc_2srcs_res_list = []
            myengine.dc_sweep(control_command, MNA_dc, RHS_dc, v_list, i_list, dc_sweep_list, dc_2srcs_res_list,
                              dc_2srcs_sweep_list, rows, col_normal, d_list, mos_list, src2, text_output)
        if control_command[0] == 'ac':
            # print "****************************ac analysis***************************************"
            text_output.insert(END, "\n****************************ac analysis***************************************")
            ac_swepp_type = control_command[1]
            # print "RHS_ac:", RHS_ac
            myengine.ac_analysis(control_command, rows, col_normal, c_list, l_list, MNA_dc,
                                 RHS_ac, ac_res_list, freq_list,text_output)
        if control_command[0] == "tran":
            text_output.insert(END, "\n****************************tran analysis*************************************")
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
            myengine.tran_analysis(control_command, MNA_tran, tran_res_list, tran_print_list, c_list, l_list,
                                   v_list, i_list, d_list, mos_list, time_list, rows, col_normal, tran_rows,text_output)

    fignum = 0
    for control_command in control_list:  # plot & print
        if control_command[0] == 'print':
            if control_command[1] == 'dc':
                for i in range(2, len(control_command)):
                    if control_command[i] == "v":
                        fignum += 1
                        plt.figure(fignum)
                        plt.ylabel("V(V)")
                        plot_voltage = []
                        node2 = 0
                        try:
                            node2 = int(control_command[i + 2])
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                        if len(dc_2srcs_res_list) == 1:
                            if node2 != 0:
                                plot_label = 'V' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'V' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in dc_2srcs_res_list[0]:
                                if node2 != 0:
                                    plot_voltage.append(v_plot[control_command[i + 1] - 1] - v_plot[node2 - 1])
                                else:
                                    plot_voltage.append(v_plot[control_command[i + 1] - 1])
                            plt.plot(dc_sweep_list, plot_voltage, label=plot_label)
                        else:
                            for i in range(len(dc_2srcs_res_list)):
                                plot_voltage = []
                                for v_plot in dc_2srcs_res_list[i]:
                                    if node2 != 0:
                                        plot_voltage.append(v_plot[control_command[i + 1] - 1] - v_plot[node2 - 1])
                                    else:
                                        plot_voltage.append(v_plot[control_command[i + 1] - 1])
                                plt.plot(dc_sweep_list, plot_voltage,
                                         label=src2[0] + '=' + str(dc_2srcs_sweep_list[i]))

                    elif control_command[i] == "i":
                        fignum += 1
                        plt.figure(fignum)
                        plt.ylabel("I(A)")
                        plot_i = []
                        for vsrc_match in v_list:
                            if vsrc_match['name'] == control_command[i + 1]:
                                if len(dc_2srcs_res_list) == 1:
                                    for i_plot in dc_2srcs_res_list[0]:
                                        plot_i.append(i_plot[vsrc_match['branch_info'] + col_normal - 1])
                                    plt.plot(dc_sweep_list, plot_i, label='i' + '(' + vsrc_match['name'] + ')')
                                    break
                                else:
                                    for i in range(len(dc_2srcs_res_list)):
                                        plot_i = []
                                        for i_plot in dc_2srcs_res_list[i]:
                                            plot_i.append(-i_plot[vsrc_match['branch_info'] + col_normal - 1])
                                        plt.plot(dc_sweep_list, plot_i,
                                                 label=src2[0] + '=' + str(dc_2srcs_sweep_list[i]))
                                    break
                    else:
                        pass
                    if dc_src1[0] == 'v':
                        plt.xlabel(dc_src1 + "(V)")
                    elif dc_src1[0] == 'i':
                        plt.xlabel(dc_src1 + "(A)")
                    plt.title("DC Transfer")
                    plt.autoscale()
                    plt.legend(loc='best')
            elif control_command[1] == 'tran':
                for i in range(2, len(control_command)):
                    if control_command[i] == "v":
                        fignum += 1
                        plt.figure(fignum)
                        plt.ylabel("V(V)")
                        plot_voltage = []
                        node2 = 0
                        try:
                            node2 = int(control_command[i + 2])
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                        if node2 != 0:
                            plot_label = 'V' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                        else:
                            plot_label = 'V' + '(' + str(control_command[i + 1]) + ')'
                        for v_plot in tran_print_list:
                            if node2 != 0:
                                plot_voltage.append(v_plot[control_command[i + 1] - 1] - v_plot[node2 - 1])
                            else:
                                plot_voltage.append(v_plot[control_command[i + 1] - 1])
                        plt.plot(time_list, plot_voltage, label=plot_label)

                    elif control_command[i] == "i":
                        fignum += 1
                        plt.figure(fignum)
                        plt.ylabel("I(A)")
                        plot_i = []
                        for vsrc_match in v_list:
                            if vsrc_match['name'] == control_command[i + 1]:
                                for i_plot in tran_print_list:
                                    plot_i.append(i_plot[vsrc_match['branch_info'] + col_normal - 1])
                                plt.plot(time_list, plot_i, label='i' + '(' + vsrc_match['name'] + ')')
                                plt.ylabel("I(A)")
                                break
                    else:
                        pass
                    plt.title("Transient Analysis")
                    plt.xlabel("t(S)")
                    plt.autoscale()
                    plt.legend(loc='best')
            elif control_command[1] == 'ac':
                for i in range(2, len(control_command)):
                    if 'v' in str(control_command[i]):
                        fignum += 1
                        plt.figure(fignum)
                        plot_voltage = []
                        node2 = 0
                        try:
                            node2 = int(control_command[i + 2])
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                        if control_command[i] == 'vr':  # real
                            plt.ylabel("V.real(V)")
                            if node2 != 0:
                                plot_label = 'VR' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'VR' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in ac_res_list:
                                v1 = v_plot[control_command[i + 1] - 1]
                                if node2 != 0:
                                    v2 = v_plot[node2 - 1]
                                    plot_voltage.append(v1.real - v2.real)
                                else:
                                    plot_voltage.append(v1.real)
                        elif control_command[i] == 'vi':  # imag
                            plt.ylabel("V.imag(V)")
                            if node2 != 0:
                                plot_label = 'VI' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'VI' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in ac_res_list:
                                v1 = v_plot[control_command[i + 1] - 1]
                                if node2 != 0:
                                    v2 = v_plot[node2 - 1]
                                    plot_voltage.append(v1.imag - v2.imag)
                                else:
                                    plot_voltage.append(v1.imag)
                        elif control_command[i] == 'vp':
                            plt.ylabel("phase(degree)")
                            if node2 != 0:
                                plot_label = 'VP' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'VP' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in ac_res_list:
                                v1 = v_plot[control_command[i + 1] - 1]
                                if node2 != 0:
                                    v2 = v_plot[node2 - 1]
                                    phase2 = 180 * math.atan2(v1.imag - v2.imag, v1.real - v2.real) / math.pi
                                    plot_voltage.append(phase2)
                                else:
                                    phase1 = 180 * math.atan2(v1.imag, v1.real) / math.pi
                                    plot_voltage.append(phase1)
                        elif control_command[i] == 'vdb':
                            plt.ylabel("V(dB)")
                            if node2 != 0:
                                plot_label = 'VDB' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'VDB' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in ac_res_list:
                                v1 = v_plot[control_command[i + 1] - 1]
                                if node2 != 0:
                                    v2 = v_plot[node2 - 1]
                                    plot_voltage.append(20 * math.log10(abs(v1 - v2)))
                                else:
                                    plot_voltage.append(20 * math.log10(abs(v1)))
                        elif control_command[i] == 'v' or control_command[i] == 'vm':
                            plt.ylabel("V(V)")
                            if node2 != 0:
                                plot_label = 'VM' + '(' + str(control_command[i + 1]) + ',' + str(node2) + ')'
                            else:
                                plot_label = 'VM' + '(' + str(control_command[i + 1]) + ')'
                            for v_plot in ac_res_list:
                                v1 = v_plot[control_command[i + 1] - 1]
                                if node2 != 0:
                                    v2 = v_plot[node2 - 1]
                                    plot_voltage.append(abs(v1 - v2))
                                else:
                                    plot_voltage.append(abs(v1))
                        else:
                            pass
                        if ac_swepp_type == 'dec':
                            plt.semilogx(freq_list, plot_voltage, label=plot_label)
                        elif ac_swepp_type == 'oct':
                            plt.plot(freq_list, plot_voltage, label=plot_label)
                        else:
                            plt.plot(freq_list, plot_voltage, label=plot_label)
                    elif 'i' in str(control_command[i]):
                        fignum += 1
                        plt.figure(fignum)
                        plot_i = []
                        for vsrc_match in v_list:
                            if vsrc_match['name'] == control_command[i + 1]:
                                if 'r' in control_command[i]:  # real
                                    plt.ylabel("i.real(A)")
                                    plot_label = 'IR' + '(' + vsrc_match['name'] + ')'
                                    for i_plot in ac_res_list:
                                        i1 = i_plot[vsrc_match['branch_info'] + col_normal - 1]
                                        plot_i.append(i1.real)
                                elif 'i' in control_command[i]:  # imag
                                    plt.ylabel("i.imag(A)")
                                    plot_label = 'II' + '(' + vsrc_match['name'] + ')'
                                    for i_plot in ac_res_list:
                                        i1 = i_plot[vsrc_match['branch_info'] + col_normal - 1]
                                        plot_i.append(i1.imag)
                                elif 'p' in control_command[i]:
                                    plt.ylabel("phase(°)")
                                    plot_label = 'IP' + '(' + vsrc_match['name'] + ')'
                                    for i_plot in ac_res_list:
                                        i1 = i_plot[vsrc_match['branch_info'] + col_normal - 1]
                                        phase = 180 * math.atan2(i1.imag, i1.real) / math.pi
                                        plot_i.append(phase)
                                elif 'db' in control_command[i]:
                                    plt.ylabel("i(dB)")
                                    plot_label = 'IDB' + '(' + vsrc_match['name'] + ')'
                                    for i_plot in ac_res_list:
                                        i1 = i_plot[vsrc_match['branch_info'] + col_normal - 1]
                                        plot_i.append(20 * math.log10(abs(i1)))
                                else:
                                    plt.ylabel("i(i)")
                                    plot_label = 'IM' + '(' + vsrc_match['name'] + ')'
                                    for i_plot in ac_res_list:
                                        i1 = i_plot[vsrc_match['branch_info'] + col_normal - 1]
                                        plot_i.append(abs(i1))
                                if ac_swepp_type == 'dec':
                                    plt.semilogx(freq_list, plot_i, label=plot_label)
                                elif ac_swepp_type == 'oct':
                                    plt.plot(freq_list, plot_i, label=plot_label)
                                else:
                                    plt.plot(freq_list, plot_i, label=plot_label)
                    else:
                        pass
                    plt.title("AC Analysis")
                    plt.xlabel("freq(Hz)")
                    plt.autoscale()
                    plt.legend(loc='best')

    if fignum != 0:
        plt.show()
    # return  plt
if __name__ == '__main__':
    filename = raw_input("please enter netlist filename:")
    engine(filename)
