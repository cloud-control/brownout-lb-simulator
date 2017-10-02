%% get avgs and 95% confidence intervals
repeats = 20;
samplespersec = 2.0;
trialtime = 400.0;
totallength = 16000;
replicas = 3;


responsetimes(responsetimes == 0.0) = NaN;

times = times(1:totallength, :);
responsetimes = responsetimes(1:totallength, :);
inner_setpoints = inner_setpoints(1:totallength, :);
avgqueue_lengths = avgqueue_lengths(1:totallength, :);
queue_lengths = queue_lengths(1:totallength, :);
expdimmers = expdimmers(1:totallength, :);
v = v(1:totallength, :);


avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

respavg = zeros(length(avgtimes), replicas);
setpointavg = zeros(length(avgtimes), replicas);
avgqueueavg = zeros(length(avgtimes), replicas);
queueavg = zeros(length(avgtimes), replicas);
expdimmersavg = zeros(length(avgtimes), replicas);
vavg = zeros(length(avgtimes), replicas);
queuediffavg = zeros(length(avgtimes), replicas);

respconf = zeros(length(avgtimes), 2*replicas);
setpointconf = zeros(length(avgtimes), 2*replicas);
avgqueueconf = zeros(length(avgtimes), 2*replicas);
queueconf = zeros(length(avgtimes), 2*replicas);
expdimconf = zeros(length(avgtimes), 2*replicas);
vconf = zeros(length(avgtimes), 2*replicas);
queuediffconf = zeros(length(avgtimes), 2*replicas);

l = 1; % conf int index variable


for k = 1:replicas
     
    
    for i = 1:max(avgt)-1

        j = i - 1;
        if j == 0
            j = 1;
        end

        indexes = find(mod(1:length(times),max(avgt))==i);
        indexes_j = find(mod(1:length(times),max(avgt))==j);

        respavg(i, k) = nanmean(responsetimes(indexes, k));
        setpointavg(i, k) = nanmean(inner_setpoints(indexes, k));
        avgqueueavg(i, k) = nanmean(avgqueue_lengths(indexes, k));
        queueavg(i, k) = nanmean(queue_lengths(indexes, k));
        expdimmersavg(i, k) = nanmean(expdimmers(indexes, k));
        vavg(i, k) = nanmean(v(indexes, k));
        queuediffavg(i, k) = nanmean(queue_lengths(indexes, k) - queue_lengths(indexes_j, k));


        respconf(i, l:(l+1)) = confint(responsetimes(indexes, k));
        setpointconf(i, l:(l+1)) = confint(inner_setpoints(indexes, k));
        avgqueueconf(i, l:(l+1)) = confint(avgqueue_lengths(indexes, k));
        queueconf(i, l:(l+1)) = confint(queue_lengths(indexes, k));
        expdimconf(i, l:(l+1)) = confint(expdimmers(indexes, k));
        vconf(i, l:(l+1)) = confint(v(indexes, k));
        queuediffconf(i, l:(l+1)) = confint(queue_lengths(indexes, k) - queue_lengths(indexes_j, k));



    end
    
    l = l + 2;

end