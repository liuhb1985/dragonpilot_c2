#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_8950913116326216966);
void live_err_fun(double *nom_x, double *delta_x, double *out_4711982804252955032);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_987015477252924114);
void live_H_mod_fun(double *state, double *out_1832924919917867232);
void live_f_fun(double *state, double dt, double *out_1588828596107137082);
void live_F_fun(double *state, double dt, double *out_2183639023472067723);
void live_h_4(double *state, double *unused, double *out_7741022990868701262);
void live_H_4(double *state, double *unused, double *out_4161851496746342480);
void live_h_9(double *state, double *unused, double *out_477664504040557478);
void live_H_9(double *state, double *unused, double *out_3125367438518104990);
void live_h_10(double *state, double *unused, double *out_6443228509142062934);
void live_H_10(double *state, double *unused, double *out_8874910200408772308);
void live_h_12(double *state, double *unused, double *out_330079982949843112);
void live_H_12(double *state, double *unused, double *out_3505276816936108012);
void live_h_35(double *state, double *unused, double *out_8790711799983117858);
void live_H_35(double *state, double *unused, double *out_6250839849261121721);
void live_h_32(double *state, double *unused, double *out_2150611208290271285);
void live_H_32(double *state, double *unused, double *out_9034498013679539314);
void live_h_13(double *state, double *unused, double *out_2092287283304078636);
void live_H_13(double *state, double *unused, double *out_5001853691059707633);
void live_h_14(double *state, double *unused, double *out_477664504040557478);
void live_H_14(double *state, double *unused, double *out_3125367438518104990);
void live_h_33(double *state, double *unused, double *out_3861496358533257555);
void live_H_33(double *state, double *unused, double *out_9045347219809572291);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}