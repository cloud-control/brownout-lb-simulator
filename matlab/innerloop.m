s = tf('s');

%C = 5;

C = minreal(10*(s+0.5)/(s+5));

G = 1/s;

T = minreal(feedback(C*G,1));

S = minreal(1-T);

CS = minreal(C*S);

PS = minreal(G*S);

L = minreal(C*G);

margin(L)

