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
void live_H(double *in_vec, double *out_2960658737492787476);
void live_err_fun(double *nom_x, double *delta_x, double *out_1168693363665656049);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8516324702579607987);
void live_H_mod_fun(double *state, double *out_5050531981406926292);
void live_f_fun(double *state, double dt, double *out_6593654468520165468);
void live_F_fun(double *state, double dt, double *out_8336444242967279575);
void live_h_4(double *state, double *unused, double *out_5676980825581654730);
void live_H_4(double *state, double *unused, double *out_2751568970240603784);
void live_h_9(double *state, double *unused, double *out_6162087004563154205);
void live_H_9(double *state, double *unused, double *out_8407956168204500362);
void live_h_10(double *state, double *unused, double *out_80717491852991391);
void live_H_10(double *state, double *unused, double *out_7520462595821763171);
void live_h_12(double *state, double *unused, double *out_4857928348417781350);
void live_H_12(double *state, double *unused, double *out_3372667995288197451);
void live_h_35(double *state, double *unused, double *out_1444730968879020233);
void live_H_35(double *state, double *unused, double *out_6118231027613211160);
void live_h_32(double *state, double *unused, double *out_6284422972132118645);
void live_H_32(double *state, double *unused, double *out_518820614746128927);
void live_h_13(double *state, double *unused, double *out_1714284400569732566);
void live_H_13(double *state, double *unused, double *out_5582004668101593438);
void live_h_14(double *state, double *unused, double *out_6162087004563154205);
void live_H_14(double *state, double *unused, double *out_8407956168204500362);
void live_h_33(double *state, double *unused, double *out_147193260364713348);
void live_H_33(double *state, double *unused, double *out_9177956041457482852);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}