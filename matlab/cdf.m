function F = cdf(x)

sigma = 0.02;
mu1 = 0.01;
tau = 0.10;
N = 1000;
xmax = 0.2;
h = xmax/N;

x2 = x;

%pdf = (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x2-tau).^2/(2*sigma.^2)-x2./mu);
pdf = (1/(sigma.*sqrt(2.*pi))).*exp(-(x2-tau).^2/(2*sigma.^2));
norm = sum(pdf)*h;
%pdf = pdf./norm;
%f = @(x) (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2)-x./mu)./norm;
f = @(x) (1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2))./norm;

F = zeros(size(x));
for j=1:length(x)
   F(j) = integral(f,0,x(j));
end

end