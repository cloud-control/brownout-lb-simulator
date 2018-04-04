%% get avgs and 95% confidence intervals
repeats = 20;
samplespersec = 4.0;
trialtime = 250.0;
totallength = 5000;
replicas = 5;

lbtimes2 = lbtimes(1001:end);
optResponseTimes2 = optResponseTimes(1001:end);

optResponseTimes2(optResponseTimes2 == 0.0) = NaN;

waitingTimes2 = waitingTimes(1001:end);
waitingQueue2 = waitingQueue(1001:end);
queueSetpoints2 = queueSetpoints(1001:end);

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*(avgt-1);

avgtimes = avgtimes';

respavg = zeros(length(avgtimes), 1);
respconf = zeros(length(avgtimes), 2);

queueavg = zeros(length(avgtimes), 1);
queueconf = zeros(length(avgtimes), 2);

waitingtimeavg = zeros(length(avgtimes), 1);
waitingtimeconf = zeros(length(avgtimes), 2);

queuesetpointavg= zeros(length(avgtimes), 1);
queuesetpointconf = zeros(length(avgtimes), 2);


l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        indexes = find(mod(1:length(lbtimes2),max(avgt))==i);
        
        respavg(i) = nanmean(optResponseTimes2(indexes));
        respconf(i, l:(l+1)) = confint(optResponseTimes2(indexes));
        
        queueavg(i) = nanmean(waitingQueue2(indexes));
        queueconf(i, l:(l+1)) = confint(waitingQueue2(indexes));
        
        waitingtimeavg(i) = nanmean(waitingTimes2(indexes));
        waitingtimeconf(i, l:(l+1)) = confint(waitingTimes2(indexes));
        
        queuesetpointavg(i) = nanmean(queueSetpoints2(indexes));
        queuesetpointconf(i, l:(l+1)) = confint(queueSetpoints2(indexes));

    end