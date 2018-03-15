clc
close all;

s = tf('s');

Gp = 1/s;
GN = 1;
GD = s;

% control design to get good behavior against load disturbances
% how to formalize this? define z and omega for the poles, and then it is a
% pole placement acording to that parameterization!
kp = 1.5;
ki = 0.6;

Gc = minreal(kp + ki/s);

Gcl = minreal(Gc*Gp/(1+Gc*Gp))

old_poles = pole(Gcl)
old_zeros = zero(Gcl)

% reference weighting to get better reference following transient
beta = 0.6;

Gclhat = minreal((GN*ki+kp*GN*beta*s)/((GD+GN*kp)*s+GN*ki))

new_poles = pole(Gclhat)
new_zeros = zero(Gclhat)

% plotting
figure()
step(Gcl, 'b')
hold on
step(Gclhat, 'r')