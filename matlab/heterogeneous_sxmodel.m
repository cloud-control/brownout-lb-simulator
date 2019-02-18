%% Hyperexp + dolly analysis
clear all;
clc;
dollycdf = zeros(12, 1);

dollypdf = zeros(12,1);
dollypdf(1) = 0.230; dollypdf(2) = 0.140; dollypdf(3) = 0.09;
dollypdf(4) = 0.03; dollypdf(5) = 0.08; dollypdf(6) = 0.10;
dollypdf(7) = 0.04; dollypdf(8) = 0.140; dollypdf(9) = 0.12;
dollypdf(10) = 0.021; dollypdf(11) = 0.007; dollypdf(12) = 0.002;

hypermeanservicetime = 1/4.7;
hypercoeff = 10;
arrivalcoeff = 1;


dollycdf(1) = 0.230;dollycdf(2) = 0.370;dollycdf(3) = 0.460;
dollycdf(4) = 0.490;dollycdf(5) = 0.570;dollycdf(6) = 0.670;
dollycdf(7) = 0.710;dollycdf(8) = 0.850;dollycdf(9) = 0.970;
dollycdf(10) = 0.991;dollycdf(11) = 0.998;dollycdf(12) = 1.000;

dollycdf2 = zeros(2*length(dollycdf), 1);
dollycdf4 = zeros(4*length(dollycdf), 1);

for i=1:11
    dollycdf2(i*2) = dollycdf(i);
    dollycdf2(i*2+1) = dollycdf(i);
    dollycdf4(i*4) = dollycdf(i);
    dollycdf4(i*4+1) = dollycdf(i);
    dollycdf4(i*4+2) = dollycdf(i);
    dollycdf4(i*4+3) = dollycdf(i);
end

dollycdf2(24) = dollycdf(12);
dollycdf4(48) = dollycdf(12);

dollypdf2 = zeros(size(dollycdf2));
dollypdf4 = zeros(size(dollycdf4));

for i=2:length(dollycdf2)
    dollypdf2(i) = dollycdf2(i) - dollycdf2(i-1);
end

for i=2:length(dollycdf4)
    dollypdf4(i) = dollycdf4(i) - dollycdf4(i-1);
end

plot(dollycdf)
hold on;
plot(dollycdf2)

figure()
stem(dollypdf2)

sum(dollypdf2);
sum(dollypdf4);

x1 = [1:12]';
x2 = [1:24]';
x4 = [1:48]';

% Case 1

dollymean1 = cumsum(x1.*dollypdf);
m10 = dollymean1(end)

dollym21 = cumsum(x1.^2.*dollypdf);
mm10 = dollym21(end)

% Case 2

dollymean2 = cumsum(x2.*dollypdf2);
m20 = dollymean2(end)

dollym22 = cumsum(x2.^2.*dollypdf2);
mm20 = dollym22(end)

% % Case 4
% 
% dollymean4 = cumsum(x4.*dollypdf4);
% m40 = dollymean4(end)
% 
% dollym24 = cumsum(x4.^2.*dollypdf4);
% mm40 = dollym24(end)
% 
% c1 = (m21 - m10^2)/(m10^2);
% c2 = (m22 - m20^2)/(m20^2);
% c4 = (m24 - m40^2)/(m40^2);


% Case 1-1

mindollycdf11 = 1 - (1 - dollycdf).*(1 - dollycdf);

mindollypdf11 = zeros(size(mindollycdf11'));

mindollypdf11(1) = mindollycdf11(1);
for i=2:length(mindollycdf11)
    mindollypdf11(i) = mindollycdf11(i) - mindollycdf11(i-1);
end

cloneminmean11 = cumsum(x1.*mindollypdf11');
m11 = cloneminmean11(end)
cloneminquadexp11 = cumsum((x1.^2).*mindollypdf11');
mm11 = cloneminquadexp11(end)



% Case 1-2

mindollycdf12 = 1 - (1 - dollycdf).*(1 - dollycdf2(1:12));
mindollypdf12 = zeros(size(mindollycdf12'));

mindollypdf12(1) = mindollycdf12(1);
for i=2:length(mindollycdf12)
    mindollypdf12(i) = mindollycdf12(i) - mindollycdf12(i-1);
end


cloneminmean12 = cumsum(x1.*mindollypdf12');
m12 = cloneminmean12(end)
cloneminquadexp12 = cumsum((x1.^2).*mindollypdf12');
mm12 = cloneminquadexp12(end)

% Case 1-4

% mindollycdf14 = 1 - (1 - dollycdf).*(1 - dollycdf4(1:12));
% mindollypdf14 = zeros(size(mindollycdf14'));
% 
% mindollypdf14(1) = mindollycdf14(1);
% for i=2:length(mindollycdf14)
%     mindollypdf14(i) = mindollycdf14(i) - mindollycdf14(i-1);
% end
% 
% 
% cloneminmean14 = cumsum(x1.*mindollypdf14');
% m14 = cloneminmean14(end)


% Case 2-2

mindollycdf22 = 1 - (1 - dollycdf2).*(1 - dollycdf2);
mindollypdf22 = zeros(size(mindollycdf22'));

mindollypdf22(1) = mindollycdf22(1);
for i=2:length(mindollycdf22)
    mindollypdf22(i) = mindollycdf22(i) - mindollycdf22(i-1);
end

cloneminmean22 = cumsum(x2.*mindollypdf22');
m22 = cloneminmean22(end)
cloneminquadexp22 = cumsum((x2.^2).*mindollypdf22');
mm22 = cloneminquadexp22(end)


% Case 1-1-2-2

mindollycdf1122 = 1 - (1 - dollycdf).*(1 - dollycdf2(1:12)).*(1 - dollycdf).*(1 - dollycdf2(1:12));
mindollypdf1122 = zeros(size(mindollycdf1122'));

mindollypdf1122(1) = mindollycdf1122(1);
for i=2:length(mindollycdf1122)
    mindollypdf1122(i) = mindollycdf1122(i) - mindollycdf1122(i-1);
end


cloneminmean1122 = cumsum(x1.*mindollypdf1122');
m1122 = cloneminmean1122(end)
cloneminquadexp1122 = cumsum((x1.^2).*mindollypdf1122');
mm1122 = cloneminquadexp1122(end)

% % Case 4-4
% 
% mindollycdf44 = 1 - (1 - dollycdf4).*(1 - dollycdf4);
% mindollypdf44 = zeros(size(mindollycdf44'));
% 
% mindollypdf44(1) = mindollycdf44(1);
% for i=2:length(mindollycdf44)
%     mindollypdf44(i) = mindollycdf44(i) - mindollycdf44(i-1);
% end
% 
% cloneminmean44 = cumsum(x4.*mindollypdf44');
% m44 = cloneminmean44(end)

%% Use M/G/1 to analyze the heterogeneous systems

clc;

lambdas = 4.*[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];

respTimes = zeros(9, 4);

for i=1:9
    
    lambda = lambdas(i)
    
    % Case 1
    
    lambda10 = lambda*1/3;

    avgservicetime = hypermeanservicetime* m10
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm10 - (hypermeanservicetime*m10).^2
    servicecoeff = vartot/((hypermeanservicetime*m10).^2)
    util = lambda10*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T10 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T10 = -1;
    end
    
    
    % Case 2
    
    lambda20 = lambda*1/6;

    avgservicetime = hypermeanservicetime* m20
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm20 - (hypermeanservicetime*m20).^2
    servicecoeff = vartot/((hypermeanservicetime*m20).^2)
    util = lambda20*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T20 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T20 = -1;
    end
    
    respTimes(i,4) = (2/3)*T10 + (1/3)*T20
    
    
    % Case 1-1
    
    lambda11 = lambda*2/3;

    avgservicetime = hypermeanservicetime* m11
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm11 - (hypermeanservicetime*m11).^2
    servicecoeff = vartot/((hypermeanservicetime*m11).^2)
    util = lambda11*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T11 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T11 = -1;
    end
    
    
     % Case 2-2
    
    lambda22 = lambda*1/3;

    avgservicetime = hypermeanservicetime* m22
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm22 - (hypermeanservicetime*m22).^2
    servicecoeff = vartot/((hypermeanservicetime*m22).^2)
    util = lambda22*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T22 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T22 = -1;
    end
    
    respTimes(i,1) = (2/3)*T11 + (1/3)*T22
    
    
    % Case 1-2
    
    lambda12 = lambda*1/2;

    avgservicetime = hypermeanservicetime* m12
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm12 - (hypermeanservicetime*m12).^2
    servicecoeff = vartot/((hypermeanservicetime*m12).^2)
    util = lambda12*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T12 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T12 = -1;
    end
    
    respTimes(i,2) = T12
    
    
    % Case 1-1-2-2
    
    lambda1122 = lambda;

    avgservicetime = hypermeanservicetime* m1122
    vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*mm1122 - (hypermeanservicetime*m1122).^2
    servicecoeff = vartot/((hypermeanservicetime*m1122).^2)
    util = lambda1122*avgservicetime

    if util <= 1
        %minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
        T1122 = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util))
        %minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
    else
        T1122 = -1;
    end
    
    respTimes(i,3) = T1122
    
    
    
end








 %%

%mindollycdf = 1 - (1 - dollycdf).^nbrClones;

%mindollypdf = zeros(size(mindollycdf));

%mindollypdf(1) = mindollycdf(1);

%for i=2:length(mindollycdf)
%    mindollypdf(i) = mindollycdf(i) - mindollycdf(i-1);
%end
x = [1:12]';

dollymean = cumsum(x.*dollypdf);

hypermeanservicetime = 1/4.7;
hypercoeff = 10;
arrivalcoeff = 1;

rates = 0.00:0.001:1.0000;
%arrivalrate = 0.05;

minmeans = zeros(1,50);
minquadexp = zeros(1,50);
mincoeffs = zeros(1,50);
minavgresps = -1*ones(1,50);
minavgresps2 = -1*ones(1,50);

optclones = ones(size(rates));
meanRTs = zeros(size(rates));

index = 0;

utils = zeros(length(rates), 12);

for lambda = rates

index = index + 1;
clones = 1:12;
for j = clones
nbrClones = j;
mindollycdf = 1 - (1 - dollycdf).^nbrClones;
mindollypdf = zeros(size(mindollycdf));

mindollypdf(1) = mindollycdf(1);

for i=2:length(mindollycdf)
    mindollypdf(i) = mindollycdf(i) - mindollycdf(i-1);
end

cloneminmean = cumsum(x.*mindollypdf);

cloneminvar = cumsum((x.^2).*mindollypdf) - cumsum(x.*mindollypdf);
cloneminquadexp = cumsum((x.^2).*mindollypdf);

minmeans(j) = cloneminmean(end);
minquadexp(j) = cloneminquadexp(end);
mincoeffs(j) = cloneminvar(end)./(cloneminmean(end).^2);

% Use kingmans formula for G/G/1
avgservicetime = hypermeanservicetime* cloneminmean(end);
vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*minquadexp(j) - (hypermeanservicetime*minmeans(j)).^2;
servicecoeff = vartot/((hypermeanservicetime*minmeans(j)).^2);
util = lambda*avgservicetime*j;

if util <= 1
    utils(index, j) = lambda;
    minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
    %minavgresps2(j) = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util));
    minavgresps2(j) = 1./((1./avgservicetime) - (lambda*j));
end

end

minresp = min(minavgresps(minavgresps>0));
bestCloningKingman = find(minavgresps == minresp);

minresp2 = min(minavgresps2(minavgresps2>0))
bestCloningMG1 = find(minavgresps2 == minresp2)
shortestResponseTime = minresp2

optclones(index) = bestCloningMG1;
meanRTs(index) = shortestResponseTime;

end

plot(rates, optclones)
figure()
plot(rates, meanRTs)
figure()
plot(rates, utils)
hold on;
plot(rates, rates)
