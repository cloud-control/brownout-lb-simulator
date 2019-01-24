close all;
clear all;
clc;
mu = 1;
max_slow = 2;
N = 100000;
nbrClones = 2;
samples = zeros(N, nbrClones);
s_samples = zeros(N, nbrClones);

for i=1:N
    % Draw inherent task size
    x = exprnd(mu,1,1);
    
    % Draw server slowdown
    s = 1 + (max_slow - 1)*rand(1, nbrClones);
    
    s_samples(i,:) = s;
    samples(i,:) = x.*s;
    
end

xedge = linspace(0,10*mu*max_slow, 20000)';
yedge = xedge;
x = xedge(1:end-1);

cdfs = zeros(length(xedge)-1, nbrClones);
s_cdfs = zeros(length(xedge)-1, nbrClones);

for j=1:nbrClones
    [f,~] = histcounts(samples(:,j), xedge, 'Normalization', 'cdf');
    cdfs(:,j) = f;
    
    [fs,~] = histcounts(s_samples(:,j), xedge, 'Normalization', 'cdf');
    s_cdfs(:,j) = fs;
end

%figure()
%plot(x,cdfs)

[Ftemp, ~] = histcounts2(samples(:,1), samples(:,2), xedge, yedge, 'Normalization', 'cdf');

Fxy = diag(Ftemp);

%figure()
%plot(x, Fxy, 'b')
%hold on
%plot(x,cdfs(:,1), 'r')

%% Conditional probabilites

s1 = samples(:,1);
s2 = samples(:,2);

K = 10000;

avec = linspace(0,20,K);

condprobs = zeros(K,1);
firstprobs = zeros(K,1);
ind = 1;
for a = avec
i1 = find(s1<a);
s21 = s2(i1);
i2 = find(s21<a);
firstprob = length(i1)/N;
condprob = length(i2)/(length(i1));

condprobs(ind) = condprob;
firstprobs(ind) = firstprob;
ind = ind +1;

end

figure()
%plot(avec, condprobs, 'r')
hold on;
%plot(avec, firstprobs, 'b')
plot(avec, firstprobs.*condprobs, 'k')
hold on;
plot(x, Fxy, 'g--')


%% more plotting

Fx = cdfs(:,1);
Fy = cdfs(:,2);

Fxs = s_cdfs(:,1);
Fys = s_cdfs(:,2);

figure()
plot(x,Fxs, 'b');
hold on;
%plot(x,Fys, 'r');

figure()
plot(x, Fxy, 'b')
hold on
plot(x,(1-exp(-1.*x)), 'r')

Fmin = Fx + Fy - Fxy;
figure()
plot(x, Fxy,'b');
hold on;
plot(x, Fx.*Fy, 'r');

minmean = cumtrapz(x(2:end).*diff(Fmin));
mm = minmean(end)

meaners = mean(samples)

%% fit to exponential
expfit = 1-Fmin;
tester = exp(-0.60.*x);

plot(x,expfit, 'b');
hold on;
plot(x,tester, 'r');


%% Hyperexp + dolly monte carlo
clc
close all
nbrClones = 3;
M = 230330;

dolly = zeros(1000, 1);

dolly(1:230) = 1;dolly(231:370) = 2;dolly(371:460) = 3;
dolly(461:490) = 4;dolly(491:570) = 5;dolly(571:670) = 6;
dolly(671:710) = 7;dolly(711:850) = 8;dolly(851:970) = 9;
dolly(971:991) = 10;dolly(992:998) = 11;dolly(999:1000) = 12;

csvwrite('dolly.csv', dolly);

coeff = 10;
hypermean = 1/4.7;
p1 = 0.5*(1+sqrt((coeff-1)/(coeff+1)));
p2 = 1-p1;
mu1 = 2*p1/hypermean;
mu2 = 2*p2/hypermean;

sampler = zeros(M, 1);
minsampler = zeros(M, 1);
slowdowns = zeros(M,1);
for i =1:M
    %slowers = randi([1 1000], nbrClones, 1);
    slowers = zeros(nbrClones, 1);
    for j =1:nbrClones
        slowers(j) =  randi([1 1000], 1, 1);
    end
    s = dolly(slowers);
    smin = min(s);
    slowdowns(i) = smin;

    if rand() <= p1
        minsampler(i) = smin.*exprnd(1/mu1, 1, 1);
    else
        minsampler(i) = smin.*exprnd(1/mu2, 1, 1);
    end
end

samplemean = mean(minsampler)
samplecoeff = var(minsampler)/(samplemean.^2)
slowdownmean = mean(slowdowns)


%% Hyperexp + dolly analysis
clc;
dollycdf = zeros(12, 1);

dollypdf = zeros(12,1);
dollypdf(1) = 0.230; dollypdf(2) = 0.140; dollypdf(3) = 0.09;
dollypdf(4) = 0.03; dollypdf(5) = 0.08; dollypdf(6) = 0.10;
dollypdf(7) = 0.04; dollypdf(8) = 0.140; dollypdf(9) = 0.12;
dollypdf(10) = 0.021; dollypdf(11) = 0.007; dollypdf(12) = 0.002;


dollycdf(1) = 0.230;dollycdf(2) = 0.370;dollycdf(3) = 0.460;
dollycdf(4) = 0.490;dollycdf(5) = 0.570;dollycdf(6) = 0.670;
dollycdf(7) = 0.710;dollycdf(8) = 0.850;dollycdf(9) = 0.970;
dollycdf(10) = 0.991;dollycdf(11) = 0.998;dollycdf(12) = 1.000;


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
arrivalrate = 0.3;

minmeans = zeros(1,50);
minquadexp = zeros(1,50);
mincoeffs = zeros(1,50);
minavgresps = -1*ones(1,50);
minavgresps2 = -1*ones(1,50);

clones = 1:10;
for j = clones
j
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
avgservicetime = hypermeanservicetime* cloneminmean(end)
vartot = ((1+hypercoeff)*hypermeanservicetime.^2)*minquadexp(j) - (hypermeanservicetime*minmeans(j)).^2;
servicecoeff = vartot/((hypermeanservicetime*minmeans(j)).^2)
util = arrivalrate*avgservicetime*j

if util <= 1
    minavgresps(j) = avgservicetime + avgservicetime*(util/(1-util))*(arrivalcoeff + servicecoeff)/2;
    minavgresps2(j) = avgservicetime + (util*avgservicetime*(1+servicecoeff))/(2*(1-util));
end

end

minresp = min(minavgresps(minavgresps>0));
bestCloningKingman = find(minavgresps == minresp)

minresp2 = min(minavgresps2(minavgresps2>0));
bestCloningMG1 = find(minavgresps2 == minresp2)



% 
% figure()
% stem(dollycdf, 'b')
% hold on;
% stem(mindollycdf, 'r');
% 
figure()
stem(minmeans)
% 
% figure()
% stem(mincoeffs)
% 
% figure()
% stem(((50-clones)./minmeans(1) + 1./minmeans)*minmeans(1)/50)
% 
% figure()
% stem(1./(((50-clones)./minmeans(1) + 1./minmeans)*minmeans(1)/50))
% 
% figure()
% stem(mincoeffs)

figure()
stem(minavgresps, 'b')
hold on;
stem(minavgresps2, 'r')


