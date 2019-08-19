N = 5000;
x = linspace(0, 4.0, N);

mu1 = 0.48;
cdf_exp = 1-exp(-x.*mu1);

plot(x, cdf_exp)

a = 0.5;
b = 3.5;
cdf_uniform = zeros(size(x));
for i=1:length(x)
    if (x(i) >= a) && (x(i)< b)
        cdf_uniform(i) = (x(i)-a)/(b-a);
    elseif (x(i) >= b)
            cdf_uniform(i) = 1;
    end  
    
end

lambda = 2;
k = 3;
cdf_weibull =1 - exp((-x./lambda).^k);

cdf_min = 1-(1-cdf_exp).*(1-cdf_uniform).*(1-cdf_weibull);

minmean = cumtrapz(x(2:end)'.*diff(cdf_min'));
minmean(end)

plot(x, cdf_exp)
hold on;
plot(x, cdf_weibull)
plot(x, cdf_uniform)
plot(x, cdf_min)

csvwrite('mincdf.csv', [x' cdf_min']);
csvwrite('expcdf.csv', [x' cdf_exp']);
csvwrite('uniformcdf.csv', [x' cdf_uniform']);
csvwrite('weibullcdf.csv', [x' cdf_weibull']);

