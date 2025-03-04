#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_8309758392390888544);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6408703626244168062);
void car_H_mod_fun(double *state, double *out_4562515539302843936);
void car_f_fun(double *state, double dt, double *out_966800600533330194);
void car_F_fun(double *state, double dt, double *out_3165898511533365235);
void car_h_25(double *state, double *unused, double *out_3815370467301215505);
void car_H_25(double *state, double *unused, double *out_2818539797877968673);
void car_h_24(double *state, double *unused, double *out_7900774966790061249);
void car_H_24(double *state, double *unused, double *out_592832013899100111);
void car_h_30(double *state, double *unused, double *out_8043545679932040948);
void car_H_30(double *state, double *unused, double *out_2947878745021208743);
void car_h_26(double *state, double *unused, double *out_2060621840625899195);
void car_H_26(double *state, double *unused, double *out_6560043116752024897);
void car_h_27(double *state, double *unused, double *out_8988643735327379276);
void car_H_27(double *state, double *unused, double *out_5122642056821633654);
void car_h_29(double *state, double *unused, double *out_8713449673042873387);
void car_H_29(double *state, double *unused, double *out_2437647400706816559);
void car_h_28(double *state, double *unused, double *out_7077928965747953991);
void car_H_28(double *state, double *unused, double *out_474017129141490308);
void car_h_31(double *state, double *unused, double *out_818977542467304345);
void car_H_31(double *state, double *unused, double *out_2787893836001008245);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}