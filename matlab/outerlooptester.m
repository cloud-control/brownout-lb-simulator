s = tf('s');
Gn = 0.025/(s+1);
ka = 1;
C1 = ka*minreal((4.0+7.2/s));

C2 = 50;

Go = minreal(Gn*C2);

Gcl = minreal(Go/(1+Go))

poles = pole(Gcl)

step(Gcl, 'r')
hold on
T = 3.5;

G1 = 1/(1+s*T);

step(G1, 'b')

%% 
Gp = 1/s;
T = 3;
Gc = 1/T;

Go = minreal(Gp*Gc);

Gcl = minreal(Go/(1+Go))

poles = pole(Gcl)

step(Gcl, 'r')
hold on
T1 = 4.0;

G1 = 1/(1+s*T1);

step(G1, 'b')
