##!/usr/bin/env python
# ################################################################################################################
# Author: Arasch U. Lagies, Axiado
# Last Update: 12/19/2019
#
# Based on: https://github.com/zziz/kalman-filter and wickipedia (https://en.wikipedia.org/wiki/Kalman_filter)
# ################################################################################################################
# Fk, the state-transition model;
# Hk, the observation model;
# Qk, the covariance of the process noise;
# Rk, the covariance of the observation noise;
# and sometimes Bk, the control-input model, for each time-step, k, as described below.
# ################################################################################################################
# packages to install:
# conda install -c conda-forge ffmpeg
#
# Call with > python kalmanFilter6.py --dataPath Path-to-the-Coordinates

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import matplotlib.animation as animation
import matplotlib
import argparse

measurements = []
predict_x = []
predict_y = []

path = "./random.txt"

class KalmanFilter(object):
    def __init__(self, F = None, B = None, H = None, Q = None, R = None, P = None, x0 = None, y0 = None):
        if(F is None or H is None):
            raise ValueError("Set proper system dynamics.")

        self.n = F.shape[1]
        self.m = H.shape[1]

        self.F = F                      # The state-transition model
        self.H = H                      # The observation model (maps the true state space into the observed space )
        self.B = 0 if B is None else B  # The control-input model (=0 here ==> the applied model is velocity=const.)
        self.Q = np.eye(self.n) if Q is None else Q     # The covariance of the process noise
        self.R = np.eye(self.n) if R is None else R     # The covariance of the observation noise
        self.P = np.eye(self.n) if P is None else P     # a posteriori error covariance matrix (a measure of the estimated accuracy of the state estimate)
        self.x = np.zeros((self.n, 1)) if x0 is None else x0    # x-coordinate
        self.y = np.zeros((self.n, 1)) if y0 is None else y0    # y-coordinate

    def predict(self, u = 0, v = 0):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        self.y = np.dot(self.F, self.y) + np.dot(self.B, v)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        # print(f"-- u.shape = {u} --- v.shape = {v} --- x.shape = {self.x.shape} --- y.shape = {self.y.shape} --- P.shape = {self.P.shape} --- np.dot(self.F, self.x) shape = {np.dot(self.F, self.x).shape} --- np.dot(self.B, u) shape = { np.dot(self.B, u).shape}.")
        return self.x, self.y

    def update(self, zx, zy):
        yx = zx - np.dot(self.H, self.x)
        yy = zy - np.dot(self.H, self.y)
        #print(f" shape of yx = {yx.shape}, shape of zx = {zx.shape}")
        S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        #print(f"the value of S is {S} --- applying linalg.inv on it is {np.linalg.inv(S)} and the shape of K is {K.shape}")
        self.x = self.x + np.dot(K, yx)
        self.y = self.y + np.dot(K, yy)
        I = np.eye(self.n)
        #print(f" I is {I}, and the shape of KxH is {np.dot(K, self.H).shape}...")
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P), 
            (I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)

class tracking(KalmanFilter, object):
    def __init__(self):
        self.measurements = []
        self.predict_x = []
        self.predict_y = []

        self.dt = 1.0/60
        self.F = np.array([[1, self.dt, 0], [0, 1, self.dt], [0, 0, 1]])                       # the state-transition model
        self.H = np.array([1, 0, 0]).reshape(1, 3)                                   # the observation model
        self.Q = np.array([[0.005, 0.005, 0.0], [0.005, 0.005, 0.0], [0.0, 0.0, 0.0]])   # the covariance of the process noise
        self.R = np.array([1.5]).reshape(1, 1)                                       # the covariance of the observation noise
        self.kf = KalmanFilter(F = self.F, H = self.H, Q = self.Q, R = self.R)

    def kmPredict(self):
        pr_x, pr_y = self.kf.predict()
        #print(f"pr_x size is {pr_x.shape} --- pr_y size is {pr_y.shape}")
        #print(f" Result shapes: x = {np.dot(self.H,  pr_x).shape}  and for y = {np.dot(self.H,  pr_y).shape}")
        self.predict_x.append(np.dot(self.H,  pr_x)[0][0])
        self.predict_y.append(np.dot(self.H,  pr_y)[0][0])
        return pr_x, pr_y

    def kmUpdate(self, xin, yin):
        self.kf.update(xin,yin)



