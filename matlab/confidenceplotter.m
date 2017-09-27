%% get complete vector for ff

repeats = 20;
samplespersec = 2.0;
trialtime = 300.0;
totallength = 12000;

responsetimesff(responsetimesff == 0.0) = NaN;

times = times(1:totallength);
responsetimesff = responsetimesff(1:totallength);
inner_setpointsff = inner_setpointsff(1:totallength);
avgqueue_lengthsff = avgqueue_lengthsff(1:totallength);
queue_lengthsff = queue_lengthsff(1:totallength);
expdimmersff = expdimmersff(1:totallength);
v = v(1:totallength);


avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

respff = zeros(length(avgtimes), repeats);
setpointff = zeros(length(avgtimes), repeats);
avgqueueff = zeros(length(avgtimes), repeats);
queueff = zeros(length(avgtimes), repeats);
expdimff = zeros(length(avgtimes), repeats);
vff = zeros(length(avgtimes), repeats);


respffconf = zeros(length(avgtimes), 2);
setpointffconf = zeros(length(avgtimes), 2);
avgqueueffconf = zeros(length(avgtimes), 2);
queueffconf = zeros(length(avgtimes), 2);
expdimffconf = zeros(length(avgtimes), 2);
vffconf = zeros(length(avgtimes), 2);
queuediffconf = zeros(length(avgtimes), 2);


for i = 1:max(avgt)-1
   
    j = i - 1;
    if j == 0
        j = 1;
    end
    
    indexes = find(mod(1:length(times),max(avgt))==i);
    indexes_j = find(mod(1:length(times),max(avgt))==j);

    
    respavgff(i) = nanmean(responsetimesff(indexes));
    setpointavgff(i) = nanmean(inner_setpointsff(indexes));
    avgqueueavgff(i) = nanmean(avgqueue_lengthsff(indexes));
    queueavgff(i) = nanmean(queue_lengthsff(indexes));
    expdimmersavgff(i) = nanmean(expdimmersff(indexes));
    vavgff(i) = nanmean(v(indexes));
    queuediffavg(i) = nanmean(queue_lengthsff(indexes) - queue_lengthsff(indexes_j));
    
    
    respffconf(i, :) = confint(responsetimesff(indexes));
    setpointffconf(i, :) = confint(inner_setpointsff(indexes));
    avgqueueffconf(i, :) = confint(avgqueue_lengthsff(indexes));
    queueffconf(i, :) = confint(queue_lengthsff(indexes));
    expdimffconf(i, :) = confint(expdimmersff(indexes));
    vffconf(i, :) = confint(v(indexes));
    queuediffconf(i, :) = confint(queue_lengthsff(indexes) - queue_lengthsff(indexes_j));
    
   
    
end