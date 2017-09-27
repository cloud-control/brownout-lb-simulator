function CI = confint(x)
SEM = nanstd(x)/sqrt(length(x));               % Standard Error
ts = tinv([0.025  0.975],length(x)-1);      % T-Score
CI = nanmean(x) + ts*SEM;                      % Confidence Intervals