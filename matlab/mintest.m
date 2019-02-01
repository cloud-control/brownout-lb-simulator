N = 100000;
x = linspace(0, 3.1, N);

mu1 = 0.4;
cdf_exp = 1-exp(-x.*mu1);

plot(x, cdf_exp)

a = 1;
b = 3;
cdf_uniform = zeros(size(x));
for i=1:length(x)
    if (x(i) >= a) && (x(i)< b)
        cdf_uniform(i) = (x(i)-a)/(b-a);
    elseif (x(i) >= b)
            cdf_uniform(i) = 1;
    end  
    
end

mu2 = 1.8;
sigma = 0.5;
cdf_norm = 0.5*(1+erf((x-mu2)./(sigma*sqrt(2))));

cdf_min = 1-(1-cdf_exp).*(1-cdf_uniform).*(1-cdf_norm);

minmean = cumtrapz(x(2:end)'.*diff(cdf_min'));
minmean(end)

plot(x, cdf_exp)
hold on;
plot(x, cdf_uniform)
plot(x, cdf_norm)
plot(x, cdf_min)

csvwrite('mintest.csv', [x' cdf_min']);

