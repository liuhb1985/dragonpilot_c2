#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_853165848632907757);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_3474292358282872888);
void gnss_H_mod_fun(double *state, double *out_761859268784397928);
void gnss_f_fun(double *state, double dt, double *out_7046356792595204133);
void gnss_F_fun(double *state, double dt, double *out_2487464020300176341);
void gnss_h_6(double *state, double *sat_pos, double *out_2787136142504212376);
void gnss_H_6(double *state, double *sat_pos, double *out_7303003470706533198);
void gnss_h_20(double *state, double *sat_pos, double *out_7961958278524676948);
void gnss_H_20(double *state, double *sat_pos, double *out_4355378339414860987);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4606647382013950688);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_8627097252551704572);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4606647382013950688);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_8627097252551704572);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}