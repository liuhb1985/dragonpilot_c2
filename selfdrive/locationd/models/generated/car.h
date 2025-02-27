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
void car_err_fun(double *nom_x, double *delta_x, double *out_3777365459169780521);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8075421764252646021);
void car_H_mod_fun(double *state, double *out_5773449620779522412);
void car_f_fun(double *state, double dt, double *out_2232219700137468451);
void car_F_fun(double *state, double dt, double *out_8468888211654047063);
void car_h_25(double *state, double *unused, double *out_1768793091573715401);
void car_H_25(double *state, double *unused, double *out_7938114506489276154);
void car_h_24(double *state, double *unused, double *out_1160592728592438314);
void car_H_24(double *state, double *unused, double *out_5765464907483776588);
void car_h_30(double *state, double *unused, double *out_2669202737217400363);
void car_H_30(double *state, double *unused, double *out_7990296608713026835);
void car_h_26(double *state, double *unused, double *out_6351340675223076079);
void car_H_26(double *state, double *unused, double *out_4196611187615219930);
void car_h_27(double *state, double *unused, double *out_8272294162491609562);
void car_H_27(double *state, double *unused, double *out_5766702537529083618);
void car_h_29(double *state, double *unused, double *out_6870329704341152594);
void car_H_29(double *state, double *unused, double *out_7480065264398634651);
void car_h_28(double *state, double *unused, double *out_5172776643557096409);
void car_H_28(double *state, double *unused, double *out_5884279792241386391);
void car_h_31(double *state, double *unused, double *out_7368924193110135781);
void car_H_31(double *state, double *unused, double *out_3570403085381868454);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}