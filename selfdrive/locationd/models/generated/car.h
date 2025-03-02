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
void car_err_fun(double *nom_x, double *delta_x, double *out_8737444356106212750);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3396197912249715186);
void car_H_mod_fun(double *state, double *out_4408923992583434570);
void car_f_fun(double *state, double dt, double *out_6843037781789925815);
void car_F_fun(double *state, double dt, double *out_8074848689907386755);
void car_h_25(double *state, double *unused, double *out_8266765693149128178);
void car_H_25(double *state, double *unused, double *out_5740111272462494884);
void car_h_24(double *state, double *unused, double *out_1275308204301430985);
void car_H_24(double *state, double *unused, double *out_7912760871467994450);
void car_h_30(double *state, double *unused, double *out_5319039702793643217);
void car_H_30(double *state, double *unused, double *out_3221778313955246257);
void car_h_26(double *state, double *unused, double *out_1784413843384001234);
void car_H_26(double *state, double *unused, double *out_8965129482373000508);
void car_h_27(double *state, double *unused, double *out_1998555509090676087);
void car_H_27(double *state, double *unused, double *out_5396541625755671168);
void car_h_29(double *state, double *unused, double *out_7642620339575075944);
void car_H_29(double *state, double *unused, double *out_2711546969640854073);
void car_h_28(double *state, double *unused, double *out_4763020956481872404);
void car_H_28(double *state, double *unused, double *out_7793945986710384647);
void car_h_31(double *state, double *unused, double *out_6864801234998671210);
void car_H_31(double *state, double *unused, double *out_8338921380139649032);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}