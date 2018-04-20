%% get avgs and 95% confidence intervals for selected scenarios
repeats = 20;
samplespersec = 4.0;
trialtime = 250.0;

replicas = 5;

lbtimes2 = lbtimes(2001:end);
optResponseTimes95th2 = optResponseTimes95th(2001:end);

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*(avgt-1);

avgtimes = avgtimes';

optResponseTimes95thavg = zeros(length(avgtimes), 1);
optResponseTimes95thconf = zeros(length(avgtimes), 2);


l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        indexes = find(mod(1:length(lbtimes2),max(avgt))==i);
        
        optResponseTimes95thavg(i) = nanmean(optResponseTimes95th2(indexes));
        optResponseTimes95thconf(i, l:(l+1)) = confint(optResponseTimes95th2(indexes));
        

    end
%% get avgs and 95% confidence intervals for service time experiments
repeats = 20;
samplespersec = 2.0;
trialtime = 250.0;
totallength = 5000;
replicas = 5;

servertimes2 = servertimes(501:end);
serviceTimes2 = serviceTimes(501:end, 1);
ctrls2 = ctrls(501:end);
actuatedCtrls2 = actuatedCtrls(501:end);
estimatedProcessGains2 = estimatedProcessGains(501:end);

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*(avgt-1);

avgtimes = avgtimes';

serviceTimesavg = zeros(length(avgtimes), 1);
serviceTimesconf = zeros(length(avgtimes), 2);

ctrlsavg = zeros(length(avgtimes), 1);
ctrlsconf = zeros(length(avgtimes), 2);

actuatedCtrlsavg = zeros(length(avgtimes), 1);
actuatedCtrlsconf = zeros(length(avgtimes), 2);

estimatedProcessGainsavg = zeros(length(avgtimes), 1);
estimatedProcessGainsconf = zeros(length(avgtimes), 2);


l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        indexes = find(mod(1:length(servertimes2),max(avgt))==i);
        
        serviceTimesavg(i) = nanmean(serviceTimes2(indexes));
        serviceTimesconf(i, l:(l+1)) = confint(serviceTimes2(indexes));
        
        ctrlsavg(i) = nanmean(ctrls2(indexes));
        ctrlsconf(i, l:(l+1)) = confint(ctrls2(indexes));
        
        actuatedCtrlsavg(i) = nanmean(actuatedCtrls2(indexes));
        actuatedCtrlsconf(i, l:(l+1)) = confint(actuatedCtrls2(indexes));
        
        estimatedProcessGainsavg(i) = nanmean(estimatedProcessGains2(indexes));
        estimatedProcessGainsconf(i, l:(l+1)) = confint(estimatedProcessGains2(indexes));

    end
    
%% get avgs and 95% confidence intervals for waiting time experiments
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
waitingThresholds2 = waitingThresholds(1001:end);

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*(avgt-1);

avgtimes = avgtimes';

respavg = zeros(length(avgtimes), 1);
respconf = zeros(length(avgtimes), 2);

queueavg = zeros(length(avgtimes), 1);
queueconf = zeros(length(avgtimes), 2);

waitingtimeavg = zeros(length(avgtimes), 1);
waitingtimeconf = zeros(length(avgtimes), 2);

queuesetpointavg = zeros(length(avgtimes), 1);
queuesetpointconf = zeros(length(avgtimes), 2);

waitingthresholdavg = zeros(length(avgtimes), 1);
waitingthresholdconf = zeros(length(avgtimes), 2);


l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        indexes = find(mod(1:length(lbtimes2),max(avgt))==i);
        
        respavg(i) = nanmean(optResponseTimes2(indexes));
        respconf(i, l:(l+1)) = confint(optResponseTimes2(indexes));
        
        queueavg(i) = nanmean(waitingQueue2(indexes));
        queueconf(i, l:(l+1)) = confint(waitingQueue2(indexes));
        
        waitingtimeavg(i) = nanmean(waitingTimes2(indexes));
        waitingtimeconf(i, l:(l+1)) = confint(waitingTimes2(indexes));
        
        waitingthresholdavg(i) = nanmean(waitingThresholds2(indexes));
        waitingthresholdconf(i, l:(l+1)) = confint(waitingThresholds2(indexes));
        
        queuesetpointavg(i) = nanmean(queueSetpoints2(indexes));
        queuesetpointconf(i, l:(l+1)) = confint(queueSetpoints2(indexes));

    end
    
    
%% get avgs and 95% confidence intervals for distributed lb experiments
repeats = 20;
samplespersec = 2.0;
trialtime = 150.0;
totallength = 2000;
replicas = 5;

%lbtimes2 = lbtimes(501:end);
servertimes2 = servertimes(301:end);
%optResponseTimes2 = optResponseTimes(501:end);
server1ResponseTimes = optServerResponseTimes(301:end, 1);

%optResponseTimes2(optResponseTimes2 == 0.0) = NaN;
server1ResponseTimes(server1ResponseTimes == 0.0) = NaN;

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*(avgt-1);

avgtimes = avgtimes';

%respavg = zeros(length(avgtimes), 1);
%respconf = zeros(length(avgtimes), 2);

server1respavg = zeros(length(avgtimes), 1);
server1respconf = zeros(length(avgtimes), 2);




l = 1; % conf int index variable
     
    
    for i = 1:max(avgt)-1

        indexes = find(mod(1:length(servertimes2),max(avgt))==i);
        
        %respavg(i) = nanmean(optResponseTimes2(indexes));
        %respconf(i, l:(l+1)) = confint(optResponseTimes2(indexes));
        
        server1respavg(i) = nanmean(server1ResponseTimes(indexes));
        server1respconf(i, l:(l+1)) = confint(server1ResponseTimes(indexes));
        

    end