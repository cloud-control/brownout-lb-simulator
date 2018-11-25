%%
close all
clear all
mu = 100;
f = [1.2, 1.5, 1.8, 2, 2.5, 3, 3.5 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 12.5, 15, 17.5, 20, 50, 100, 1000, 10000];
N = 100000;
R = zeros(N,1);
R2 = zeros(N,1);
for j = 1:length(f)
    j
    for i = 1:N
        r1 = exprnd(mu, 1,1);
        R(i) = r1;
        r2 = -1;
        minr = r1/f(j);
        maxr = r1*f(j);
        while (r2<minr || r2>maxr)
            r2 = exprnd(mu, 1,1);
        end
        R2(i) = r2;

    end
    
    %plot(R,R2,'.');
    correr = corrcoef(R,R2);
    corre(j) = correr(1,2);
    
end
figure()
plot(f, corre);


%%
plot(f(1:end-5),corre001(1:end-5),'.r')
hold on;
plot(f(1:end-5),corre1(1:end-5),'.b')
plot(f(1:end-5),corre100(1:end-5),'.g')


%%


mu_e = 0.01;
mu_res = 0.05;
sigma = 0.01;
t = 0.10;
x = [-t:0.00001:t];
nonzero = find(x>=0);
pdf_e = zeros(size(x));
pdf_e(nonzero) = (1/mu_e)*exp(-x(nonzero)*(1/mu_e));
pdf_e_norm = pdf_e./sum(pdf_e);

pdf_n = (1/(sigma.*sqrt(2*pi))).*exp(-(x-mu_res).^2/(2*(sigma).^2));
pdf_n_norm = pdf_n./sum(pdf_n);

pdf_mix = pdf_n_norm.*pdf_e_norm;
pdf_mix_norm = pdf_mix./sum(pdf_mix);

figure()
plot(x, pdf_e_norm, 'b');
hold on;
plot(x, pdf_n_norm, 'r');
plot(x, pdf_mix_norm, 'g');
%axis([0 t 0 0.001])



%%

figure()
pdf_res = (1/mu_res)*exp(-(x-mu_res)*(1/mu_res));

pdf_mix = pdf_n.*pdf_e;

plot(x, pdf_mix./(sum(pdf_mix)), 'r')
hold on;
plot(x,pdf_e./(sum(pdf_e)), 'b')

%%

N=1000;
sigma = 0.0001;


R = exprnd(0.01, N,1);
R2 = zeros(N,1);

for i=1:N
    R2(i) = normrnd(R(i), sigma);
    
end

plot(R,R2, '.')

%%
clear all
close all
sigma = 1;
tau = 0;
y = 0.001:0.001:1;
icdf = sqrt(2).*y.*erfinv(2.*sigma-erf(tau./(sqrt(2).*y))) + tau;

plot(y,icdf)


%%
clear all;
close all;
sigma = 1;
mu1 = 0.01;
mu2 = 1;
x = [0.001:0.01:5]';
CDF = (erf((-mu1*mu2+sigma^2+mu1.*x)/(sqrt(2)*mu1*sigma))+erf((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma)))/(2*mu1);
norm = mu1*sign((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma))/(erf((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma)));
norm2 = mu1/(erf((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma)));
norm3 = (1-
CDF = CDF*norm2;
figure()
plot(x,CDF);

signer = sign((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma))
x0 = 5;
erf1 = erf((-mu1*mu2+sigma^2+mu1.*x0)/(sqrt(2)*mu1*sigma))
erf2 = erf((mu1*mu2-sigma^2)/(sqrt(2)*mu1*sigma))
summer = erf1+erf2

%%
close all
clear all
sigma = 1;
mu = 0.01;
tau = 1;
N = 10000;
xmax = 0.2;
h = xmax/N;
x = linspace(0,xmax,N);
pdf = (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2)-x./mu);
%pdf = (1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2));
norm = sum(pdf)*h;
pdf = pdf./norm;
%f = @(x) (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2)-x./mu)./norm;
f2 = @(x) (1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2))./norm;

F = zeros(size(x));
for j=1:length(x)
   %F(j) = integral(f,0,x(j));
   F(j) = my_func(x(j), sigma, mu, tau);
end

p = linspace(0,1,1000);

zero = 0;
prevFinv = 0.0;
for inc = 1:length(p)
fun = @(x)zerofinder(x,zero, sigma, mu, tau);
temp = fzero(fun,0);
if isnan(temp)
    Finv(inc) = prevFinv;
else
    Finv(inc) = fzero(fun,0);
end
zero = zero + 1/length(p);
prevFinv = Finv(inc);
end

Finv = Finv';
for inc = 1:length(p)
r = randi([2 1000]);
R2(inc) = Finv(r);
end
R2 = R2';
R = exprnd(0.01, length(p),1);




figure()
plot(p,Finv)
figure()
plot(R2, '.')
figure()
plot(x,pdf)


norm
normalized = sum(pdf)*h

correr = corrcoef(R,R2)

%%
clear all;
close all;

sigma = 1;
mu = 0.01;
M = 1;

tic()

for i = 1:M
    i
    r = exprnd(mu, 1, 1);
    R(i) = r;
    
    N = 10000;
    xmax = 0.2;
    h = xmax/N;
    x = linspace(0,xmax,N);
    pdf = (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-r).^2/(2*sigma.^2)-x./mu);
    norm = sum(pdf)*h;
    pdf = pdf./norm;
    
    F = zeros(size(x));
    for j=1:length(x)
       F(j) = my_func(x(j), sigma, mu, r);
    end

    p = linspace(0,1,1000);

    zero = 0;
    prevFinv = 0.0;
    for inc = 1:length(p)
        fun = @(x)zerofinder(x,zero, sigma, mu, r);
        temp = fzero(fun,0);
        if isnan(temp)
            Finv(inc) = prevFinv;
        else
            Finv(inc) = temp;
        end
        zero = zero + 1/length(p);
        prevFinv = Finv(inc);
    end

    r2 = randi([2 1000]);
    R2(i) = Finv(r2);
end

figure()
plot(R,R2,'.');

correr = corrcoef(R,R2)

toc()


%% Effective try for correlations
%clc
%close all;
%clear all;
tic()


mu = 0.01;
sigma = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 7.5, 10, 100,1e10];
sigma = sigma.*mu;
M = 100000;
R1 = zeros(M,1);
R2 = zeros(M,1);
corr = zeros(length(sigma),1);

xmax = 20*mu;
N = 10000;
h = xmax/N;
x_s = linspace(0,xmax,N);
progress = 0;
sig = 0;

for j = 1:1%length(sigma)
    sig = sigma(11);
    for i = 1:1
        r = exprnd(mu, 1, 1);
        R1(i) = r;
        %sig = sigma(j)*r;

        xmax = 20*r;
        h = xmax/N;
        x_s = linspace(0,xmax,N);
        pdf = exp(-(x_s-r).^2./(2*sig.^2)-x_s./mu);
        norm = sum(pdf)*h;
        pdf = pdf./norm;
        
        %if sum(isnan(pdf(:))) > 0
        %    disp('pdf has NaN');
        %    r
        %    sig
        %    error('stop here');
        %end       
        
        CDF = h*cumtrapz(pdf);    

        inverse_point = CDF(end)*rand(); % where the inverse is evaluated

        R2(i) = cdfinver(x_s, CDF, inverse_point);
    end
    
    if sum(isnan(R1(:))) > 0
        disp('R1 NaN');
    end
    if sum(isnan(R2(:))) > 0
        disp('R2 NaN');
    end

    correr = corrcoef(R1,R2);
    
    if sum(isnan(correr(:))) > 0
        disp('NaN in correr!');
    end
    corr(j) = correr(1,2);
    progress = j/length(sigma)
    
end

figure();
plot(sigma, corr, '.');
corr001_sigma10000 = corr
toc()

%% plotting 
figure()
plot(sigma(1:end), corr001_sigma(1:end), '.r');
%hold on;
%plot(sigma(1:end-1), corr1_sigmar(1:end-1), '.b');

%hold on;
%plot(sigma(1:end-3), newcorr(1:end-3), '.r');

%% Cloning 
clear all;
N = 100000;
smallest = zeros(N,1);
nbrClones = 5;
samples = zeros(nbrClones,1);
mu = 1;

for i=1:N
    samples = exprnd(mu,nbrClones,1);
    %samples = 2*rand(nbrClones,1);
    smallest(i) = min(samples);
end

cloneMean = mean(smallest);
x = linspace(0,20*mu, N);
x2 = linspace(0,2, N);

minmeans = zeros(10,1);
nvec = [1:10];
exp_cdf = 1-exp(-x./mu);
h = 20*mu/N;
mu
sig = 10000;
r = mu/1;
%sig = sig*r;
clone_pdf = exp(-((x-r).^2)./(2*sig.^2)-x./mu);
norm = sum(clone_pdf)*h;
clone_pdf = clone_pdf./norm;
clone_cdf = h*cumtrapz(clone_pdf);
%cdf = 0.5*x2;

original_cdf = zeros(size(x));
original_cdf(x>r) = 1;

mincdf_twodist = 1 - (1-original_cdf).^1.*(1-clone_cdf).^1;
minmean = h*cumtrapz(x(2:end).*diff(mincdf_twodist)./h);

mm = minmean(end)
%quota = mm/r

% for n = nvec
% 
% mincdf = 1 - (1-cdf).^n;
% 
% minmean = cumtrapz(x2(2:end).*diff(mincdf));
% 
% mm = minmean(end);
% minmeans(n) = mm;
% end

%plot(nvec,minmeans, '.')

plot(x, mincdf_twodist)


%% Mean Clone service times
clear all;

mu = 0.01;
N = 100000;
M = 100000;
xmax = 20*mu;
h = xmax/N;
x = linspace(0, xmax, N);

minmeans = zeros(M,1);
minstds = zeros(M,1);

nbrClones = 2;

sig = 1;
sig = sig*mu;

for i = 1:1%M
    %r = exprnd(mu,1,1);
    r = 0.01;
    
    xmax = 20*r;
    h = xmax/N;
    x = linspace(0, xmax, N);

    
    original_cdf = zeros(size(x));
    original_cdf(x>r) = 1;
    
    clone_pdf = exp(-((x-r).^2)./(2*sig.^2)-x./mu);
    norm = sum(clone_pdf)*h;
    clone_pdf = clone_pdf./norm;
    clone_cdf = h*cumtrapz(clone_pdf);
    
    mincdf_twodist = 1 - (1-original_cdf).^0.*(1-clone_cdf).^nbrClones;
    minmean = h*cumtrapz(x(2:end).*diff(mincdf_twodist)./h);
    %minsquaredmean = h*cumtrapz(x(2:end).^2.*diff(mincdf_twodist)./h); 
    minmeaner = minmean(end)
    %minvar = minsquaredmean(end) - minmeaner^2;
    %minstd = sqrt(minvar);
    
    minmeans(i) = minmeaner;
    %minstds(i) = minstd;
    
end

minmeans = sort(minmeans);
mm = mean(minmeans);
meanfactor = mm/mu;

plot(x, mincdf_twodist)


        
        


    
