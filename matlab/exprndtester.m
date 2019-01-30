mu = 0.6;

vec = linspace(0,10*mu, 100000)';
N = 1000000;

%cdf = zeros(length(vec)-1, 1);
samples = exprnd(mu, N, 1);

[cdf,~] = histcounts(samples, vec, 'Normalization', 'cdf');

plot(vec(1:end-1), cdf)

csvwrite('expo.csv', [vec(1:end-1) cdf']);