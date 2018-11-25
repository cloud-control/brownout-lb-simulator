function Fi = zerofinder(x, samples, CDF, zero)

if x<=0
    x = 0;
end
    Fi = interp1(samples, CDF, x) - zero;
end