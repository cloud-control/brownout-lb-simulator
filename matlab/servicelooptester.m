close all;
clc;

h = 0.5;
alpha = 0.5;
Kp = 0.05;
Kphat = 0.05;
z = tf('z', h);
s = tf('s');

a = -log(1-alpha)/h;

zeta = 0.8;
w = 1.3;

G = Kphat*(alpha*s+a)/(s+a);
Gz = Kphat*(alpha*z)/(z-1+alpha);
Ghat = d2c(Gz);


kp = (-2*zeta*w+(alpha*w^2)/a + a)/(2*zeta*w*Kp*alpha-(alpha^2*w^2*Kp)/a - Kp*a);
ki = (w^2*(1+Kp*alpha*kp))/(Kp*a);

%kp = 1;
%ki = 1;

% control design to get good behavior against load disturbances
% Keep filter pole at its original location a and move the integrator pole
% along the negative real axis!
b = 1.6;

%kp = (b*(1-alpha))/(alpha^2*b*Kp+Kp*a-Kp*alpha*a-Kp*alpha*b)
%ki = (b*(1+Kp*alpha*kp))/(Kp)



K1 = kp
K2 = 0
Ti = kp/ki
Gc1 = minreal(K1 + ki/s);
Gc2 = minreal(K2 + ki/s);

Gcl1 = minreal(zpk(Gc1*G/(1+Gc1*G)))
Gcl2 = minreal(zpk(Gc2*G/(1+Gc2*G)))

%pole(Gcl)

figure()
step(Gcl1, 'r')
hold on
step(Gcl2, 'g')


% Zero placement using reference weighting beta (probably not necessary since we will not change this reference?)
% beta = 1;
% GN = Kp*(alpha*s+a);
% GD = s+a;
% 
% Gzero = minreal(GN*ki + kp*GN*beta*s);
% 
% 
% 
% Gclhat = minreal((GN*ki+kp*GN*beta*s)/((GD+GN*kp)*s+GN*ki))
% 
% prev_zeros = zero(Gcl)
% new_zeros = zero(Gclhat)
% 
% figure()
% step(Gcl, 'r')
% hold on;
% step(Gclhat, 'b')

%step(Gz)

% figure()
% 
% step(G)
% hold on;
% step(Gz)
% 
% figure() 
% bode(G)

