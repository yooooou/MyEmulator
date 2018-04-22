# coding: utf-8
# python 2.7

import math
import numpy as np


def dc_stamp(col_normal, MNA_dc, RHS_dc, RHS_ac, v_list, i_list, d_list, mos_list, element_list, l_list, rows):
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

    return nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc, rows)

def dc_sweep(control_command, MNA_dc, v_list, i_list, dc_sweep_list, dc_2srcs_res_list,dc_2srcs_sweep_list,
             rows, col_normal, d_list, mos_list, src2_name):
    src1_n1 = 0
    src1_n2 = 0
    src1_br = 0
    RHS_base = [0] * rows
    src1 = control_command[1]
    src1_start = control_command[2]
    src1_cur_value = src1_start
    src1_end = control_command[3]
    src1_step = control_command[4]
    dc_res_list = []

    if len(control_command) == 5:                 # one src
        for vsrc in v_list:
            if vsrc['name'] !=src1 :
                br = vsrc['branch_info'] + col_normal - 1
                RHS_base[br] = vsrc['dc_value']
            else:
                src1_br = vsrc['branch_info'] + col_normal - 1
        for isrc in i_list:
            if isrc['name'] !=src1:
                n1 = isrc['node+'] - 1
                n2 = isrc['node-'] - 1
                if n1 < 0:
                    RHS_base[n2] += isrc['dc_value']
                else:
                    RHS_base[n1] += -isrc['dc_value']
                    if n2 >= 0:
                        RHS_base[n2] += isrc['dc_value']
            else:
                src1_n1 = isrc['node+'] - 1
                src1_n2 = isrc['node-'] - 1
                
        if src1[0] == "v":
            while src1_cur_value <= src1_end:
                RHS_dc_sweep = [0] * rows
                RHS_dc_sweep[src1_br] += src1_cur_value
                RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                dc_res_list.append(nonlinear_analysis(d_list,mos_list,MNA_dc,RHS_dc_sweep,rows))
                dc_sweep_list.append(src1_cur_value)
                src1_cur_value += src1_step
        else:
            while src1_cur_value <= src1_end:
                RHS_dc_sweep = [0] * rows
                if src1_n1 < 0:
                    RHS_dc_sweep[src1_n2] += src1_cur_value
                else:
                    RHS_dc_sweep[src1_n1] += - src1_cur_value
                    if src1_n2 >= 0:
                        RHS_dc_sweep[src1_n2] += src1_cur_value
                RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                dc_res_list.append(nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc_sweep, rows))
                dc_sweep_list.append(src1_cur_value)
                src1_cur_value += src1_step
        dc_2srcs_res_list.append(dc_res_list)
    else:                                         # 2 srcs
        src2_n1 = 0
        src2_n2 = 0
        src2_br = 0
        src2 = control_command[5]
        src2_cur_value = control_command[6]
        src2_end = control_command[7]
        src2_step = control_command[8]
        src2_name.append(src2)
        for vsrc in v_list:
            if vsrc['name'] == src1:
                src1_br = vsrc['branch_info'] + col_normal - 1
            elif  vsrc['name'] == src2:
                src2_br = vsrc['branch_info'] + col_normal - 1
            else:
                br = vsrc['branch_info'] + col_normal - 1
                RHS_base[br] = vsrc['dc_value']
        for isrc in i_list:
            if isrc['name'] == src1:
                src1_n1 = isrc['node+'] - 1
                src1_n2 = isrc['node-'] - 1
            elif isrc['name'] == src2:
                src2_n1 = isrc['node+'] - 1
                src2_n2 = isrc['node-'] - 1
            else:
                n1 = isrc['node+'] - 1
                n2 = isrc['node-'] - 1
                if n1 < 0:
                    RHS_base[n2] += isrc['dc_value']
                else:
                    RHS_base[n1] += -isrc['dc_value']
                    if n2 >= 0:
                        RHS_base[n2] += isrc['dc_value']
        if src2[0] == "v":
            while src2_cur_value <= src2_end:
                dc_res_list = []
                src1_cur_value = src1_start
                if src1[0] == "v":
                    while src1_cur_value <= src1_end:
                        RHS_dc_sweep = [0] * rows
                        RHS_dc_sweep[src1_br] += src1_cur_value
                        RHS_dc_sweep[src2_br] += src2_cur_value
                        RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                        dc_res_list.append(nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc_sweep, rows))
                        if src2_cur_value == control_command[6]:
                            dc_sweep_list.append(src1_cur_value)
                        src1_cur_value += src1_step
                else:
                    while src1_cur_value <= src1_end:
                        RHS_dc_sweep = [0] * rows
                        RHS_dc_sweep[src2_br] += src2_cur_value
                        if src1_n1 < 0:
                            RHS_dc_sweep[src1_n2] += src1_cur_value
                        else:
                            RHS_dc_sweep[src1_n1] += - src1_cur_value
                            if src1_n2 >= 0:
                                RHS_dc_sweep[src1_n2] += src1_cur_value
                        RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                        dc_res_list.append(nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc_sweep, rows))
                        dc_sweep_list.append(src1_cur_value)
                        if src2_cur_value == control_command[6]:
                            dc_sweep_list.append(src1_cur_value)
                dc_2srcs_res_list.append(dc_res_list)
                dc_2srcs_sweep_list.append(src2_cur_value)
                src2_cur_value += src2_step

        else:
            while src2_cur_value <= src2_end:
                dc_res_list = []
                src1_cur_value = src1_start
                if src1[0] == "v":
                    while src1_cur_value <= src1_end:
                        RHS_dc_sweep = [0] * rows
                        RHS_dc_sweep[src1_br] += src1_cur_value
                        if src2_n1 < 0:
                            RHS_dc_sweep[src2_n2] += src2_cur_value
                        else:
                            RHS_dc_sweep[src2_n1] += - src2_cur_value
                            if src2_n2 >= 0:
                                RHS_dc_sweep[src2_n2] += src2_cur_value
                        RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                        dc_res_list.append(nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc_sweep, rows))
                        if src2_cur_value == control_command[6]:
                            dc_sweep_list.append(src1_cur_value)
                        src1_cur_value += src1_step
                else:
                    while src1_cur_value <= src1_end:
                        RHS_dc_sweep = [0] * rows
                        if src1_n1 < 0:
                            RHS_dc_sweep[src1_n2] += src1_cur_value
                        else:
                            RHS_dc_sweep[src1_n1] += - src1_cur_value
                            if src1_n2 >= 0:
                                RHS_dc_sweep[src1_n2] += src1_cur_value
                        if src2_n1 < 0:
                            RHS_dc_sweep[src2_n2] += src2_cur_value
                        else:
                            RHS_dc_sweep[src2_n1] += - src2_cur_value
                            if src2_n2 >= 0:
                                RHS_dc_sweep[src2_n2] += src2_cur_value
                        RHS_dc_sweep = map(lambda (a, b): a + b, zip(RHS_dc_sweep, RHS_base))
                        dc_res_list.append(nonlinear_analysis(d_list, mos_list, MNA_dc, RHS_dc_sweep, rows))
                        if src2_cur_value == control_command[6]:
                            dc_sweep_list.append(src1_cur_value)
                        src1_cur_value += src1_step
                dc_2srcs_res_list.append(dc_res_list)
                dc_2srcs_sweep_list.append(src2_cur_value)
                src2_cur_value += src2_step

def ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, points, step, ac_res_list, freq_list, start, type):
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
        freq_list.append(freq)


def ac_analysis(control_command, rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, ac_res_list, freq_list):
    start = control_command[3]
    end = control_command[4]

    if control_command[1] == "lin":
        step = (end - start) / (control_command[2] + 1.0)
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, control_command[2] + 2,
                 step, ac_res_list, freq_list, start, "lin")

    elif control_command[1] == "dec":
        dec_start = math.log10(start)
        dec_end = math.log10(end)
        dec_step = 1 / (control_command[2] + 1.0)
        dec_points = (dec_end - dec_start) * (control_command[2] + 1) + 1
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, int(dec_points),
                 dec_step, ac_res_list, freq_list, dec_start, "dec")
    else:
        oct_start = math.log(start, 2)
        oct_end = math.log(end, 2)
        oct_step = 1 / (control_command[2] + 1.0)
        oct_points = (oct_end - oct_start) * (control_command[2] + 1) + 1
        ac_sweep(rows, col_normal, c_list, l_list, MNA_dc, RHS_ac, int(oct_points),
                 oct_step, ac_res_list, freq_list, oct_start, "oct")


def tran_analysis(control_command, MNA_tran, tran_res_list, tran_print_list,
                  c_list, l_list, v_list, i_list, d_list, mos_list, time_list, rows, col_normal, tran_rows):
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
        br_l = col_normal + l_element[-1] - 1
        MNA_tran[br_l, br_l] += -(2.0 * l_element[3]) / tmax

    # print ("tmax:%e s" % tmax)
    print ("print step:%e s" % tstep_print)
    print "MNA_tran:", MNA_tran

    time = 0

    if tstart == 0:
        time_list.append(time)
        print ("start time = %f s" % time)
        print "results:", tran_res_list[-1]
        tran_print_list.append(tran_res_list[-1])

    else:
        while time < tstart:
            last_res = tran_res_list[-1]
            RHS_tran = [0] * tran_rows
            time += tmax
            for c_element in c_list:
                n1 = c_element[1] - 1
                n2 = c_element[2] - 1
                br_c = rows + c_element[-1] - 1
                v_lt = last_res[n1]  # V(t-h)
                i_lt = last_res[br_c]  # I(t-h)
                if n2 >= 0:
                    v_lt -= last_res[n2]
                RHS_tran[br_c] += 0.5 * i_lt + v_lt * c_element[3] / float(tmax)
            for l_element in l_list:
                n1 = l_element[1] - 1
                n2 = l_element[2] - 1
                br_l = col_normal + l_element[-1] - 1
                v_lt = last_res[n1]  # V(t-h)
                i_lt = last_res[br_l]  # I(t-h)
                if n2 >= 0:
                    v_lt -= last_res[n2]
                RHS_tran[br_l] += -v_lt - 2 * i_lt * l_element[3] / float(tmax)

            pi2 = 2 * math.pi

            for vsrc in v_list:
                br = vsrc['branch_info'] + col_normal - 1
                if(vsrc['tran_type'] == "sin"):
                    RHS_tran[br] += vsrc['dc_value'] + vsrc['tran_mag'] * math.sin(pi2 * vsrc['tran_freq'] * time)
                if(vsrc['tran_type']=="pulse"):
                    slope_r = (vsrc['pulse_v2'] - vsrc['pulse_v1'])/vsrc['tr']
                    slope_f = -(vsrc['pulse_v2'] - vsrc['pulse_v1'])/vsrc['tf']
                    if time <= vsrc['td']:
                        RHS_tran[br] += vsrc['dc_value']
                    else:
                        time_in_per = time - vsrc['td'] - int((time - vsrc['td'])/vsrc['per'])*vsrc['per']
                        print "time_in_per",time_in_per
                        if time_in_per < vsrc['tr']:
                            RHS_tran[br] += vsrc['pulse_v1'] + time_in_per*slope_r
                        elif time_in_per<vsrc['tr']+vsrc['pw']:
                            RHS_tran[br] += vsrc['pulse_v2']
                        elif time_in_per<vsrc['tr']+vsrc['pw']+vsrc['tf']:
                            RHS_tran[br] += vsrc['pulse_v2'] + slope_f*(time_in_per-vsrc['tr']-vsrc['pw'])
                        else:
                            RHS_tran[br] += vsrc['pulse_v1']

            for isrc in i_list:
                n1 = isrc['node+'] - 1
                n2 = isrc['node-'] - 1
                if n1 < 0:
                    if (isrc['tran_type'] == "sin"):
                         value_plus = isrc['dc_value'] + isrc['tran_mag'] * math.sin(pi2 * isrc['tran_freq'] * time)
                    if (isrc['tran_type'] == "pulse"):
                        slope_r = (isrc['pulse_v2'] - isrc['pulse_v1']) / isrc['tr']
                        slope_f = -(isrc['pulse_v2'] - isrc['pulse_v1']) / isrc['tf']
                        if time <= isrc['td']:
                             value_plus = isrc['dc_value']
                        else:
                            time_in_per = time - isrc['td'] - int((time - isrc['td']) / isrc['per']) * isrc['per']
                            if time_in_per < isrc['tr']:
                                 value_plus = isrc['pulse_v1'] + time_in_per * slope_r
                            elif time_in_per < isrc['tr'] + isrc['pw']:
                                 value_plus = isrc['pulse_v2']
                            elif time_in_per < isrc['tr'] + isrc['pw'] + isrc['tf']:
                                 value_plus = isrc['pulse_v2'] + slope_f * (time_in_per - isrc['tr'] - isrc['pw'])
                            else:
                                 value_plus = isrc['pulse_v1']
                    RHS_tran[n2] += value_plus
                else:
                    RHS_tran[n1] += -value_plus
                    if n2 >= 0:
                        RHS_tran[n2] += value_plus

            cur_res = nonlinear_analysis(d_list, mos_list, MNA_tran, RHS_tran, tran_rows)
            # cur_res = np.linalg.solve(MNA_tran, RHS_tran)
            tran_res_list.append(cur_res)
        time_list.append(time)
        print ("start time = %f s" % time)
        print "results:", tran_res_list[-1]
        tran_print_list.append(tran_res_list[-1])

    time_n_printstep = time + tstep_print
    while time < tstop:
        last_res = tran_res_list[-1]
        RHS_tran = [0] * tran_rows
        time += tmax
        for c_element in c_list:
            n1 = c_element[1] - 1
            n2 = c_element[2] - 1
            br_c = rows + c_element[-1] - 1
            v_lt = last_res[n1]  # V(t-h)
            i_lt = last_res[br_c]  # I(t-h)
            if n2 >= 0:
                v_lt -= last_res[n2]
            RHS_tran[br_c] += 0.5 * i_lt + v_lt * c_element[3] / float(tmax)
        for l_element in l_list:
            n1 = l_element[1] - 1
            n2 = l_element[2] - 1
            br_l = col_normal + l_element[-1] - 1
            v_lt = last_res[n1]  # V(t-h)
            i_lt = last_res[br_l]  # I(t-h)
            if n2 >= 0:
                v_lt -= last_res[n2]
            RHS_tran[br_l] += -v_lt - 2 * i_lt * l_element[3] / float(tmax)

        pi2 = 2 * math.pi

        for vsrc in v_list:
            br = vsrc['branch_info'] + col_normal - 1
            if(vsrc['tran_type'] == "non"):
                RHS_tran[br] += vsrc['dc_value']
            if (vsrc['tran_type'] == "sin"):
                RHS_tran[br] += vsrc['dc_value'] + vsrc['tran_mag'] * math.sin(pi2 * vsrc['tran_freq'] * time)
            if (vsrc['tran_type'] == "pulse"):
                slope_r = (vsrc['pulse_v2'] - vsrc['pulse_v1']) / vsrc['tr']
                slope_f = -(vsrc['pulse_v2'] - vsrc['pulse_v1']) / vsrc['tf']
                if time <= vsrc['td']:
                    RHS_tran[br] += vsrc['dc_value']
                else:
                    time_in_per = time - vsrc['td'] - int((time - vsrc['td']) / vsrc['per']) * vsrc['per']
                    print "time_in_per", time_in_per
                    if time_in_per < vsrc['tr']:
                        RHS_tran[br] += vsrc['pulse_v1'] + time_in_per * slope_r
                    elif time_in_per < vsrc['tr'] + vsrc['pw']:
                        RHS_tran[br] += vsrc['pulse_v2']
                    elif time_in_per < vsrc['tr'] + vsrc['pw'] + vsrc['tf']:
                        RHS_tran[br] += vsrc['pulse_v2'] + slope_f * (time_in_per - vsrc['tr'] - vsrc['pw'])
                    else:
                        RHS_tran[br] += vsrc['pulse_v1']

        for isrc in i_list:
            n1 = isrc['node+'] - 1
            n2 = isrc['node-'] - 1
            if n1 < 0:
                if (isrc['tran_type'] == "non"):
                    value_plus += isrc['dc_value']
                if (isrc['tran_type'] == "sin"):
                    value_plus = isrc['dc_value'] + isrc['tran_mag'] * math.sin(pi2 * isrc['tran_freq'] * time)
                if (isrc['tran_type'] == "pulse"):
                    slope_r = (isrc['pulse_v2'] - isrc['pulse_v1']) / isrc['tr']
                    slope_f = -(isrc['pulse_v2'] - isrc['pulse_v1']) / isrc['tf']
                    if time <= isrc['td']:
                        value_plus = isrc['dc_value']
                    else:
                        time_in_per = time - isrc['td'] - int((time - isrc['td']) / isrc['per']) * isrc['per']
                        if time_in_per < isrc['tr']:
                            value_plus = isrc['pulse_v1'] + time_in_per * slope_r
                        elif time_in_per < isrc['tr'] + isrc['pw']:
                            value_plus = isrc['pulse_v2']
                        elif time_in_per < isrc['tr'] + isrc['pw'] + isrc['tf']:
                            value_plus = isrc['pulse_v2'] + slope_f * (time_in_per - isrc['tr'] - isrc['pw'])
                        else:
                            value_plus = isrc['pulse_v1']
                RHS_tran[n2] += value_plus
            else:
                RHS_tran[n1] += -value_plus
                if n2 >= 0:
                    RHS_tran[n2] += value_plus

        cur_res = nonlinear_analysis(d_list, mos_list, MNA_tran, RHS_tran, tran_rows)
        # cur_res = np.linalg.solve(MNA_tran, RHS_tran)
        tran_res_list.append(cur_res)
        if time >= time_n_printstep:
            time_list.append(time)
            print " "
            print ("time = %e s" % time)
            print "RHS_tran:", RHS_tran
            print "results:", cur_res
            tran_print_list.append(cur_res)
            time_n_printstep += tstep_print


def nonlinear_analysis(d_list, mos_list, MNA_base, RHS_base, rows):
    if (len(d_list) == 0 )and (len(mos_list) == 0):
        print "linear"
        print "MNA:", MNA_base
        print "RHS:", RHS_base
        res = np.linalg.solve(MNA_base, RHS_base)
        print "results:", res
    else:
        # print "Nonlinear"
        flag = 0
        times = 1
        while flag == 0:
            flag = 1
            MNA_nonlinear = np.zeros((rows, rows))
            RHS_nonlinear = [0] * rows
            if len(d_list) != 0:
                for d_element in d_list:
                    n1 = d_element[1] - 1
                    n2 = d_element[2] - 1
                    if times == 1:
                        vd = 0.1
                        flag = 0
                    elif times == 2:
                        vd = res[n1]
                        if n2 >= 0:
                            vd -= res[n2]
                        vd_last = 0.1
                        if abs(vd - vd_last) > 0.02 * abs(vd_last):
                            flag = 0
                    else:
                        vd = res[n1]
                        vd_last = res_last[n1]
                        if n2 >= 0:
                            vd -= res[n2]
                            vd_last -= res_last[n2]
                        if abs(vd - vd_last) > 0.02 * abs(vd_last):
                            flag = 0
                    G0 = 40 * math.exp(40 * vd)
                    I0 = -G0 * vd + math.exp(40 * vd) - 1
                    MNA_nonlinear[n1, n1] += G0
                    RHS_nonlinear[n1] += -I0
                    if n2 >= 0:
                        MNA_nonlinear[n1, n2] += -G0
                        MNA_nonlinear[n2, n1] += -G0
                        MNA_nonlinear[n2, n2] += G0
                        RHS_nonlinear[n2] += I0

            if len(mos_list) != 0:
                for mos_element in mos_list:
                    drain_node = mos_element['drain'] - 1
                    source_node = mos_element['source'] - 1
                    gate_node = mos_element['gate'] - 1
                    # body_node = mos_element['body'] - 1
                    width = mos_element['width']
                    length = mos_element['length']

                    if times == 1:
                        if mos_element['model_name'] == 'nmos':
                            vgs = 0
                        else:
                            vgs = -1.8
                        vds = 0
                        flag = 0
                    else:
                        vgs = res[gate_node]
                        vds = res[drain_node]
                        if source_node >= 0:
                            vgs -= res[source_node]
                            vds -= res[source_node]
                        if times == 2:
                            vgs_last = 0.7
                            vds_last = 0
                        else:
                            vgs_last = res_last[gate_node]
                            vds_last = res_last[drain_node]
                            if source_node >= 0:
                                vgs_last -= res_last[source_node]
                                vds_last -= res_last[source_node]

                        if (abs(vgs - vgs_last) > 0.02 * abs(vgs_last)) or (abs(vds - vds_last) > 0.02 * abs(vds_last)):
                            flag = 0

                    if mos_element['model_name'] == 'nmos':
                        vt0 = 0.43
                        # gamma = 0.4
                        # phi = 0.6
                        k = 1.15e-4
                        Lambda = 0.06
                        vov = vgs - vt0
                        if vov > 0:
                            if (vds <= vov) and (vds > 0):
                                ids = k * (vov * vds - 0.5 * vds * vds) * (1 + Lambda * vds) * width / length
                                gm = k * vds * (1 + Lambda * vds) * width / length
                                gds = k * (vov + (2 * Lambda * vov - 1) * vds - 1.5 * Lambda * vds * vds) * width / length
                            elif vds > vov:
                                ids = 0.5 * k * vov * vov * (1 + Lambda * vds) * width / length
                                gm = k * vds * vov * width / length
                                gds = Lambda * ids
                            else:
                                ids = k * (vov * vds - 0.5 * vds * vds) * width / length
                                gm = k * vds * width / length
                                gds = k * (vov - vds) * width / length
                        else:
                            ids = 0
                            gm = 0
                            gds = 0
                    else:
                        vt0 = -0.4
                        # gamma = -0.4
                        # phi = 0.6
                        k = -3.0e-5
                        Lambda = -0.1
                        vov = vgs - vt0
                        if vov < 0:
                            if (vds >= vov) and (vds < 0):
                                ids = k * (vov * vds - 0.5 * vds * vds) * (1 + Lambda * vds) * width / length
                                gm = k * vds * (1 + Lambda * vds) * width / length
                                gds = k * (vov + (2 * Lambda * vov - 1) * vds - 1.5 * Lambda * vds * vds) * width / length
                            elif vds < vov:
                                ids = 0.5 * k * vov * vov * (1 + Lambda * vds) * width / length
                                gm = k * vds * vov * width / length
                                gds = Lambda * ids
                            else:
                                ids = k * (vov * vds - 0.5 * vds * vds) * width / length
                                gm = k * vds * width / length
                                gds = k * (vov - vds) * width / length
                        else:
                            ids = 0
                            gm = 0
                            gds = 0

                    I0 = ids - gm * vgs - gds * vds
                    MNA_nonlinear[drain_node, drain_node] += gds
                    MNA_nonlinear[drain_node, gate_node] += gm
                    RHS_nonlinear[drain_node] += -I0
                    if source_node >= 0:
                        MNA_nonlinear[drain_node, source_node] += -gds - gm
                        MNA_nonlinear[source_node, source_node] += gds + gm
                        MNA_nonlinear[source_node, drain_node] += -gds
                        MNA_nonlinear[source_node, gate_node] += -gm
                        RHS_nonlinear[source_node] += I0

            if flag == 1:
                print "final results:", res
                break

            MNA_nonlinear += MNA_base
            RHS_nonlinear = map(lambda (a, b): a + b, zip(RHS_nonlinear, RHS_base))
            if times > 1:
                res_last = res
            res = list(np.linalg.solve(MNA_nonlinear, RHS_nonlinear))
            print "times:", times
            print "MNA:", MNA_nonlinear
            print "RHS:", RHS_nonlinear
            print "results:", res
            times += 1
    return res
