%% Case 1, lambda = 15, muM = 20, mu0 = 10
data = [0.200209	0.0
0.335882	0.1
0.445923	0.15
0.661486	0.2
0.755411	0.22
0.966773	0.24
1.292689	0.26
1.879519	0.28
2.996139	0.3
3.805482	0.31
6.673087	0.32
20.897041	0.33];

lambda = 15; muM = 20; muO = 10;

thetas_exp = data(:,2);
t_exp = data(:,1);

thetas = 0:0.01:0.33;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;

figure(1)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 15, \mu_M = 20, \mu_O = 10')
xlabel('\theta')
ylabel('Response time')

%% Case 2, lambda = 18, muM = 20, muO = 10
data = [0.498690	0.0
0.569286	0.01
0.646966	0.02
0.726331	0.03
0.836801	0.04
0.999641	0.05
1.191029	0.06
1.476211	0.07
2.177138	0.08
2.838722	0.09
5.143262	0.1];

lambda = 18; muM = 20; muO = 10;

thetas_exp = data(:,2);
t_exp = data(:,1);

thetas = 0:0.01:0.1;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;

figure(2)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 18, \mu_M = 20, \mu_O = 10')
xlabel('\theta')
ylabel('Response time')


%% Case 3, lambda = 12, muM = 20, muO = 10
data = [0.124654	0.0
0.168971	0.1
0.231329	0.2
0.323117	0.3
0.485127	0.4
0.834520	0.5
0.938225	0.52
1.054496	0.54
1.381846	0.56
1.728479	0.58
2.272587	0.6
2.439631	0.61
2.719892	0.62
4.956761	0.63
6.045373	0.64
6.901075	0.65];

lambda = 12; muM = 20; muO = 10;

thetas_exp = data(:,2);
t_exp = data(:,1);

thetas = 0:0.01:0.65;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;


figure(3)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 12, \mu_M = 20, \mu_O = 10')
xlabel('\theta')
ylabel('Response time')

%% Case 4, lambda = 75, muM = 100, muO = 50
data = [0.039905	0.0
0.067742	0.1
0.074773	0.12
0.083519	0.14
0.096627	0.16
0.110738	0.18
0.134106	0.2
0.153068	0.22
0.201784	0.24
0.256441	0.26
0.278537	0.27
0.370693	0.28
0.435710	0.29
0.604983	0.3
0.899812	0.31];

lambda = 75; muM = 100; muO = 50;

thetas_exp = data(:,2);
t_exp = data(:,1);

thetas = 0:0.01:0.31;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;

figure(5)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 75, \mu_M = 100, \mu_O = 50')
xlabel('\theta')
ylabel('Response time')

%% Case 5, lambda = 15, muM = 200, muO = 10
data = [0.005402	0.0
0.033882	0.1
0.072511	0.2
0.124159	0.3
0.216340	0.4
0.446356	0.5
1.370213	0.6];

lambda = 15; muM = 200; muO = 10;

thetas_exp = data(:,2);
t_exp = data(:,1);

thetas = 0:0.01:0.6;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;

figure(5)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 15, \mu_M = 200, \mu_O = 10')
xlabel('\theta')
ylabel('Response time')

%% Case 6
data = [0.0 0.001 0.001
0.1 0.020 0.021
0.2 0.043 0.043
0.3 0.068 0.068
0.4 0.099 0.097
0.5 0.132 0.133
0.6 0.179 0.179
0.7 0.245 0.242
0.8 0.329 0.339
0.9 0.563 0.518
1.0 1.040 1.000];

lambda = 9; muM = 1000; muO = 10;

thetas_exp = data(:,1);
t_exp = data(:,2);

thetas = 0:0.01:1;
mu = 1./((1-thetas)/muM+thetas/muO);
rho = lambda./mu;
V = 2*(1-thetas)/muM^2+2*thetas/muO^2-1./mu.^2;
t_pk = (rho+mu*lambda.*V)./(2*(mu-lambda))+1./mu;

mueff = 1./((1-thetas)./muM+thetas./muO);
t_theory = 1./(mueff-lambda)+1./mueff;

figure(6)
plot(thetas,t_theory,'b',thetas,t_pk,'r',thetas_exp,t_exp,'r+')
title('\lambda = 9, \mu_M = 1000, \mu_O = 10')
xlabel('\theta')
ylabel('Response time')