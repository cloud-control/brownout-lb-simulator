%% get avgs and 95% confidence intervals
repeats = 5;
samplespersec = 2.0;
trialtime = 200.0;
totallength = 1000;
replicas = 5;

lbtimes2 = lbtimes(302:end);
optResponseTimes2 = optResponseTimes(302:end);

optResponseTimes2(optResponseTimes2 == 0.0) = NaN;

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

%avgtimes = avgtimes';

respavg = zeros(length(avgtimes), 1);

respconf = zeros(length(avgtimes), 2);


l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        j = i - 1;
        if j == 0
            j = 1;
        end

        indexes = find(mod(1:length(lbtimes2),max(avgt))==i);
        respavg(i) = nanmean(optResponseTimes2(indexes));

        respconf(i, l:(l+1)) = confint(optResponseTimes2(indexes));

    end