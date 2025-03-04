#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_1837430737556375840);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_6703320248771398317);
void gnss_H_mod_fun(double *state, double *out_7223525491420160642);
void gnss_f_fun(double *state, double dt, double *out_5667714537195954906);
void gnss_F_fun(double *state, double dt, double *out_6767885670201210831);
void gnss_h_6(double *state, double *sat_pos, double *out_5335731577245849412);
void gnss_H_6(double *state, double *sat_pos, double *out_3192658576878514520);
void gnss_h_20(double *state, double *sat_pos, double *out_5071065378358447233);
void gnss_H_20(double *state, double *sat_pos, double *out_6970922785903045969);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_2785026116624926359);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_6283179567948606894);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_2785026116624926359);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_6283179567948606894);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}