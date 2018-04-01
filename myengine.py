# coding: utf-8
# python 2.7

import math
import numpy as np

# import matplotlib.pyplot as plt

def dc_stamp(col_normal, MNA_dc, RHS_dc, RHS_ac, v_list, i_list, element_list, l_list):
    for vsrc in v_list:
        n1 = vsrc['node+'] - 1
        n2 = vsrc['node-'] - 1
        br = vsrc['branch_info'] + col_normal
        RHS_dc[br - 1] = vsrc['dc_value']
        RHS_ac[br - 1] = vsrc['ac_mag']
        MNA_dc[n1, br - 1] += 1
        MNA_dc[br - 1, n1] += 1
        if n2 >= 0:
            MNA_dc[n2, br - 1] += -1
            MNA_dc[br - 1, n2] += -1

    for isrc in i_list:
        n1 = isrc['node+'] - 1
        n2 = isrc['node-'] - 1
        if n1 < 0:
            RHS_dc[n2] += isrc['dc_value']
            RHS_ac[n2] += isrc['ac_mag']
        else:
            RHS_dc[n1] += -isrc['dc_value']
            RHS_ac[n1] += -isrc['ac_mag']
            if n2 >= 0:
                RHS_dc[n2] += isrc['dc_value']
                RHS_ac[n2] += isrc['ac_mag']

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


def ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, points, step, ac_res_list, omega_list, start, type):
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


def ac_analysis(control_command, rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, ac_res_list, omega_list):
    start = control_command[3]
    end = control_command[4]

    if control_command[1] == "lin":
        step = (end - start) / (control_command[2] + 1.0)
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, control_command[2] + 2,
                 step, ac_res_list, omega_list, start, "lin")

    elif control_command[1] == "dec":
        dec_start = math.log10(start)
        dec_end = math.log10(end)
        dec_step = 1 / (control_command[2] + 1.0)
        dec_points = (dec_end - dec_start) * (control_command[2] + 1) + 1
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, int(dec_points),
                 dec_step, ac_res_list, omega_list, dec_start, "dec")
    else:
        oct_start = math.log(start, 2)
        oct_end = math.log(end, 2)
        oct_step = 1 / (control_command[2] + 1.0)
        oct_points = (oct_end - oct_start) * (control_command[2] + 1) + 1
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, int(oct_points),
                 oct_step, ac_res_list, omega_list, oct_start, "oct")


def tran_analysis(control_command, MNA_tran, tran_res_list,
                  c_list, l_list, v_list, i_list, time_list, rows, col_normal, tran_rows):
    tstep_print = control_command[1]
    tstop = control_command[2]
    if len(control_command) > 3:
        tstart = control_command[3]
    else:
        tstart = 0
    if len(control_command) > 4:
        tmax = control_command[4]
    else:
        tmax = tstep_print
        tmax_cmp = (tstop - tstart) / 50.0
        if tstep_print > tmax_cmp:
            tmax = tmax_cmp

    for c_element in c_list:
        n1 = c_element[1] - 1
        n2 = c_element[2] - 1
        br_c = rows + c_element[-1] - 1
        MNA_tran[n1][br_c] += 1
        MNA_tran[br_c][n1] += c_element[3] / float(tmax)
        MNA_tran[br_c][br_c] += -0.5
        if n2 >= 0:
            MNA_tran[n2][br_c] += -1
            MNA_tran[br_c][n2] += -c_element[3] / float(tmax)

    for l_element in l_list:
        br_l = rows + l_element[-1] - 1
        MNA_tran[br_l , br_l ] += -(2.0 * l_element[3]) / tmax

    time = 0
    while time <= tstop :
        RHS_tran = [0] * tran_rows
        time += tmax
        last_res = tran_res_list[-1]
        for c_element in c_list:
            n1 = c_element[1] - 1
            n2 = c_element[2] - 1
            br_c = rows + c_element[-1] - 1
            v_lt = last_res[n1]        # Vt-h
            i_lt = last_res[br_c]      # It-h
            if n2>=0:
                v_lt -= last_res[n2]
            RHS_tran[br_c] += 0.5 * i_lt + v_lt * c_element[3] / float(tmax)

        for l_element in l_list:
            n1 = l_element[1] - 1
            n2 = l_element[2] - 1
            br_l = rows + l_element[-1] - 1
            v_lt = last_res[n1]        # Vt-h
            i_lt = last_res[br_l]      # It-h
            if n2>=0:
                v_lt -= last_res[n2]
            RHS_tran[br_l] +=  -v_lt - 2*i_lt * l_element[3] / float(tmax)
        
        pi2 = 2*math.pi
        
        for vsrc in v_list:
            br = vsrc['branch_info'] + col_normal - 1
            RHS_tran[br] += vsrc['dc_value'] + vsrc['tran_mag']*math.sin(pi2*vsrc['tran_freq']*time)

        for isrc in i_list:
            n1 = isrc['node+'] - 1
            n2 = isrc['node-'] - 1
            if n1 < 0:
                RHS_tran[n2] += isrc['dc_value'] + isrc['tran_mag']*math.sin(pi2*isrc['tran_freq']*time)
            else:
                RHS_tran[n1] += -isrc['dc_value'] + isrc['tran_mag']*math.sin(pi2*isrc['tran_freq']*time)
                if n2 >= 0:
                    RHS_tran[n2] += isrc['dc_value'] + isrc['tran_mag']*math.sin(pi2*isrc['tran_freq']*time)
            
        
        cur_res = np.linalg.solve(MNA_tran, RHS_tran)
        tran_res_list.append(cur_res)
        time += tmax



