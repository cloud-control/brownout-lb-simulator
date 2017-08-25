%% Outer loop control design

s = tf('s');

% process parameters
T = 1;
G = 1/(1+s/3);
P = minreal(1/(1+s*T));
%control parameters

K = 1;
Ti = 0.5*wc;

C = minreal(K*(1+1/(s*Ti)));

L = minreal(P*C)

pole(L)

%% pole placement for static model
close all
clc
s = tf('s');
P = 0.05;

w0 = 0.2609;


ki = 6
kp = ki/w0 - 1/P

C = minreal(kp+ki/s);

Gcl = minreal(feedback(P*C,1));

S = minreal(feedback(1,C*P));

PS = minreal(P*S);
CS = minreal(C*S);

p = pole(Gcl)

z = zero(Gcl)

%step(Gcl)

bodemag(CS)

% figure
% bodemag(Gcl)
% 
% figure
% bodemag(S)
% 
% figure
% bodemag(PS)


Ms = norm(S,inf)

%bodemag(Gcl)


%% pole placement for first order model

s = tf('s');
clc
%for i=1:50
zeta = 1;
%w0 = i*0.1;
w0 = 0.6;
T = 1;
K = 0.05;

P = minreal(K/(1+s*T));

kp = (2*zeta*w0*T - 1)/K
ki = (w0^2*T)/K

%kp = 0.5/K
%ki = 0.5/K

Kffs = kp

Tiffs = kp/ki

C = minreal(kp+ki/s);

Gcl = minreal(feedback(C*P,1));
Gcl2 = minreal(feedback(C*P*200,1));
Gcl3 = minreal(feedback(C*P/200,1));

%step(Gcl)
%hold on;
%step(Gcl2)
%step(Gcl3)
%hold off

Gcl

poles = pole(Gcl)

S = minreal(feedback(1,C*P));
Ms = norm(S,inf)
Mt = norm(Gcl, inf)
%bode(S)

%omega(i) = w0;
%Ms(i) = norm(S,inf);

%end
%figure
%plot(omega,Ms);

% T = minreal(feedback(C*P,1));
% 
% figure()
% bodemag(T)
% 
% CS = minreal(C*S);
% figure()
% bodemag(CS, {0.001, 10000})

%figure
%bodemag(P*S)

%figure
%step(P*S)
%% Plotting for first order model
wmin = 0.001;
wmax = 1000;

subplot(3,1,1)
% plot bode
margin(C*P)

subplot(3,1,2)
% plot S
S = minreal(feedback(1,C*P));

looptransfer = loopsens(P,C); 
Snom = looptransfer.Si;
Ms = norm(Snom,inf)

bodemag(S, {wmin, wmax})


subplot(3,1,3)
% plot T
T = minreal(feedback(C*P,1));

bodemag(T, {wmin, wmax})
