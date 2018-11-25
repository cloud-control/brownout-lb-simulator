function Fi = my_func(i, sigma, mu, tau, xmax)

N = 10000;
h = xmax/N;

x = linspace(0,xmax,N);


pdf = (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2)-x./mu);
%pdf = (1/(sigma.*sqrt(2.*pi))).*exp(-(x2-tau).^2/(2*sigma.^2));
norm = sum(pdf)*h;
%pdf = pdf./norm;
f = @(x) (1/mu).*(1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2)-x./mu)./norm;
%f = @(x) (1/(sigma.*sqrt(2.*pi))).*exp(-(x-tau).^2/(2*sigma.^2))./norm;

Fi = integral(f,0,i);

end