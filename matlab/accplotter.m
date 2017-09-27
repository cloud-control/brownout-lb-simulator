

close all;
clear;
clc;

%% Get total response time data

experiment_dir2 = '/local/home/tommi/CloudControl/ACC2018/brownout-lb-simulator//results/trivial/single/';
server_files2 = dir([experiment_dir2, '/sim-server*-ctl-tommi.csv']);
filename2 = server_files2(1).name;
content2 = csvread([experiment_dir2, '/', filename2]);
optionalTimesmm = content2(:,1);


%% Get simulation data
experiment_dir = '/local/home/tommi/CloudControl/ACC2018/brownout-lb-simulator//results/trivial/single/';
server_files = dir([experiment_dir, '/sim-server*-ctl.csv']);
num_replicas = length(server_files);
dimmer_values_newavg = [];

for i = 1:num_replicas
    
    filename = server_files(i).name;
    content = csvread([experiment_dir, '/', filename]);
    
%     file sim-serverX-ctl.csv contains:
%     (1) time, 
%     (2) nbr of latency samples per ctrl interval, 
%     (3) max_latency (or nan), 
%     (4) dimmer value,
%     (5) dimmer value with nan if replica is inactive
    
    %getting data
    times= content(:, 1);
    resp = content(:,2);
    responsetimesff(:,i) = resp;
    np95_lat = content(:,3);
    np95_latencies(:, i) = np95_lat;
    np95_lat_long = content(:,4);
    np95_latencies_long(:, i) = np95_lat_long;
    np95_lat_short = content(:,5);
    np95_latencies_short(:, i) = np95_lat_short;
    queue = content(:,6);
    queue_lengthsff(:,i) = queue;
    avgqueue = content(:,7);
    avgqueue_lengthsff(:,i) = avgqueue;
    inner = content(:, 8);
    inner_setpointsff(:, i) = inner;
    arr = content(:,9);
    arrivals(:,i) = arr;
    arrhat = content(:,10);
    arrivalshat(:,i) = arrhat;
    dim = content(:,11);
    avgdimmers(:,i) = dim;
    expdim = content(:,12);
    expdimmersff(:,i) = expdim;
    fb = content(:,13);
    feedback(:,i) = fb;
    ff = content(:,14);
    feedforward(:,i) = ff;
    alph = content(:,15);
    alpha(:,i) = alph;
    gh = content(:,16);
    ghat(:,i) = gh;
    vx = content(:,17);
    v(:,i) = vx;
    qthresh = content(:,18);
    queueLengthThreshold(:,i) = qthresh;
    
end

%% Get real data
experiment_dir = '/local/home/tommi/CloudControl/ACC2018/real-experiments/period-0-5/new-inner-loop-2/';
server_files = dir([experiment_dir, '/controller.csv']);
num_replicas = length(server_files);
dimmer_values_newavg = [];

for i = 1:num_replicas
    
    filename = server_files(i).name;
    content = csvread([experiment_dir, '/', filename]);
    
%     file sim-serverX-ctl.csv contains:
%     (1) time, 
%     (2) nbr of latency samples per ctrl interval, 
%     (3) max_latency (or nan), 
%     (4) dimmer value,
%     (5) dimmer value with nan if replica is inactive
    
    %getting data
    times= content(:, 1);
    resp = content(:,2);
    responsetimesreal(:,i) = resp;
    np95_lat = content(:,3);
    np95_latencies(:, i) = np95_lat;
    np95_lat_long = content(:,4);
    np95_latencies_long(:, i) = np95_lat_long;
    np95_lat_short = content(:,5);
    np95_latencies_short(:, i) = np95_lat_short;
    queue = content(:,6);
    queue_lengthsreal(:,i) = queue;
    avgqueue = content(:,7);
    avgqueue_lengthsreal(:,i) = avgqueue;
    inner = content(:, 8);
    inner_setpointsreal(:, i) = inner;
    arr = content(:,9);
    arrivals(:,i) = arr;
    arrhat = content(:,10);
    arrivalshat(:,i) = arrhat;
    dim = content(:,11);
    avgdimmers(:,i) = dim;
    expdim = content(:,12);
    expdimmersreal(:,i) = expdim;
    fb = content(:,13);
    feedback(:,i) = fb;
    ff = content(:,14);
    feedforward(:,i) = ff;
    alph = content(:,15);
    alpha(:,i) = alph;
    gh = content(:,16);
    ghat(:,i) = gh;
    vx = content(:,17);
    v(:,i) = vx;
    qthresh = content(:,18);
    queueLengthThreshold(:,i) = qthresh;
    
end


%% plot open loop

np95_latencies_long3(np95_latencies_long3 == 0.0) = NaN;
np95_latencies_short3(np95_latencies_short3 == 0.0) = NaN;

avgt = 1:200;

avgtimes = 0.5.*avgt;

for i = 0:199


    indexes = find(mod(1:length(times),200)==i);
    
    
    if i < 3
        longavg3(198+i) = nanmean(np95_latencies_long3(indexes));
        shortavg3(198+i) = nanmean(np95_latencies_short3(indexes));
    else
        longavg3(i-2) = nanmean(np95_latencies_long3(indexes));
        shortavg3(i-2) = nanmean(np95_latencies_short3(indexes));
    end
    

    
end
longavg3(1) = NaN;
subplot(2,1,1)
plot(avgtimes, longavg, '.b')
hold on;
plot(avgtimes, shortavg, '.r')
subplot(2,1,2)
hold on;
plot(avgtimes, longavg3, '.k')
plot(avgtimes, shortavg3, '.g')
hold off;

%% get transient experiments for ff and fb

responsetimesff(responsetimesff == 0.0) = NaN;

samplespersec = 2.0;
trialtime = 300.0;

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

for i = 0:599


    indexes = find(mod(1:length(times),600)==i);
    
    
    if i < 3
        respavgff(598+i) = nanmean(responsetimesff(indexes));
        setpointavgff(598+i) = nanmean(inner_setpointsff(indexes));
        avgqueueavgff(598+i) = nanmean(avgqueue_lengthsff(indexes));
        queueavgff(max(avgt)-2+i) = nanmean(queue_lengthsff(indexes));
        expdimmersavgff(max(avgt)-2+i) = nanmean(expdimmersff(indexes));
        vavgff(max(avgt)-2+i) = nanmean(v(indexes));
    else
        
        respavgff(i-2) = nanmean(responsetimesff(indexes));
        setpointavgff(i-2) = nanmean(inner_setpointsff(indexes));
        avgqueueavgff(i-2) = nanmean(avgqueue_lengthsff(indexes));
        queueavgff(i-2) = nanmean(queue_lengthsff(indexes));
        expdimmersavgff(i-2) = nanmean(expdimmersff(indexes));
        vavgff(i-2) = nanmean(v(indexes));
    end
      
end

diffqueueavgff = diff(queueavgff);

%% get transient for fb

responsetimesfb(responsetimesfb == 0.0) = NaN;

samplespersec = 2.0;
trialtime = 300.0;

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

for i = 0:max(avgt)-1


    indexes = find(mod(1:length(times),max(avgt))==i);
    
    if i < 3
        respavgfb(max(avgt)-2+i) = nanmean(responsetimesfb(indexes));
        setpointavgfb(max(avgt)-2+i) = nanmean(inner_setpointsfb(indexes));
        avgqueueavgfb(max(avgt)-2+i) = nanmean(avgqueue_lengthsfb(indexes));
        queueavgfb(max(avgt)-2+i) = nanmean(queue_lengthsfb(indexes));
        expdimmersavgfb(max(avgt)-2+i) = nanmean(expdimmersfb(indexes));
        vavgfb(max(avgt)-2+i) = nanmean(v(indexes));
    else
        
        respavgfb(i-2) = nanmean(responsetimesfb(indexes));
        setpointavgfb(i-2) = nanmean(inner_setpointsfb(indexes));
        avgqueueavgfb(i-2) = nanmean(avgqueue_lengthsfb(indexes));
        queueavgfb(i-2) = nanmean(queue_lengthsfb(indexes));
        expdimmersavgfb(i-2) = nanmean(expdimmersfb(indexes));
        vavgfb(i-2) = nanmean(v(indexes));
    end
    

    
end

diffqueueavgfb = diff(queueavgfb);

%% get transient for mm

%responsetimesmm(responsetimesmm == 0.0) = NaN;

avgt = 1:600;

avgtimes = 0.5.*avgt;

for i = 0:599


    indexes = find(mod(1:length(times),600)==i);
    
    
    if i < 3
        respavgmm(598+i) = nanmean(responsetimesmm(indexes));
        setpointavgmm(598+i) = nanmean(inner_setpointsmm(indexes));
        queueavgmm(598+i) = nanmean(avgqueue_lengthsmm(indexes));
    else
        
        respavgmm(i-2) = nanmean(responsetimesmm(indexes));
        setpointavgmm(i-2) = nanmean(inner_setpointsmm(indexes));
        queueavgmm(i-2) = nanmean(avgqueue_lengthsmm(indexes));
    end
    

    
end

%% get transient for real fb

responsetimesreal(responsetimesreal == 0.0) = NaN;

samplespersec = 2.0;
trialtime = 300.0;

avgt = 1:trialtime*samplespersec;

avgtimes = 1/samplespersec*avgt;

for i = 0:max(avgt)-1


    indexes = find(mod(1:length(times),max(avgt))==i);
    
    if i < 3
        respavgreal(max(avgt)-2+i) = nanmean(responsetimesreal(indexes));
        setpointavgreal(max(avgt)-2+i) = nanmean(inner_setpointsreal(indexes));
        avgqueueavgreal(max(avgt)-2+i) = nanmean(avgqueue_lengthsreal(indexes));
        queueavgreal(max(avgt)-2+i) = nanmean(queue_lengthsreal(indexes));
        expdimmersavgreal(max(avgt)-2+i) = nanmean(expdimmersreal(indexes));
        vavgreal(max(avgt)-2+i) = nanmean(v(indexes));
    else
        
        respavgreal(i-2) = nanmean(responsetimesreal(indexes));
        setpointavgreal(i-2) = nanmean(inner_setpointsreal(indexes));
        avgqueueavgreal(i-2) = nanmean(avgqueue_lengthsreal(indexes));
        queueavgreal(i-2) = nanmean(queue_lengthsreal(indexes));
        expdimmersavgreal(i-2) = nanmean(expdimmersreal(indexes));
        vavgreal(i-2) = nanmean(v(indexes));
    end
    

    
end

diffqueueavgreal = diff(queueavgreal);

%% plot statistically significant real transients

subplot(4,1,1)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
plot(avgtimes, expdimmersreal(1:max(avgt)), 'b')
%plot(avgtimes, expdimmersavgfb, 'b')
%plot(avgtimes, expdimmersff(1:600), 'r')
%plot(avgtimes, vavgreal, 'b')
%plot(avgtimes, [0 diffqueueavgreal], 'r')
axis([0 300 0 1])
hold off

subplot(4,1,2)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
%plot(avgtimes, expdimmersreal(1:max(avgt)), 'b')
%plot(avgtimes, expdimmersavgfb, 'b')
%plot(avgtimes, expdimmersff(1:600), 'r')
plot(avgtimes, vavgreal, 'b')
%plot(avgtimes, [0 diffqueueavgreal], 'r')
%axis([0 300 0 1])
hold off

subplot(4,1,3)
hold on
%plot(avgtimes, queueavgmm, '.g')
plot(avgtimes, queueavgreal, 'b')
%plot(avgtimes, setpointavgff, 'r')
plot(avgtimes, setpointavgreal, 'k')
%plot(avgtimes, queueavgff, '.r')
axis([0 300 0 50])
hold off;

subplot(4,1,4)
hold on;
plot(avgtimes, 1.0*ones(size(avgtimes)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
plot(avgtimes, respavgreal, 'b')
%plot(avgtimes, respavgff, 'r')
axis([0 300 0 2])



hold off;

%% plot statistically significant transients

subplot(3,1,1)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
%plot(avgtimes, expdimmersfb(1:max(avgt)), 'b')
%plot(avgtimes, vavgff, 'r')
%plot(avgtimes(1:599), [queuediffavg], 'r')
%ciplot(queuediffconf(:,1), queuediffconf(:,2), avgtimes, 'r',0.5);
%plot(avgtimes(1:599), vavgff, 'b')
%ciplot(vffconf(:,1), vffconf(:,2), avgtimes, 'b',0.5);
%plot(avgtimes, [0 diffqueueavgff], 'r')
plot(avgtimes(1:599), expdimmersavgff(1:599), 'k')
%plot(avgtimes, expdimmersff(1:600), 'r')
axis([0 300 0 1])
hold off

subplot(3,1,2)
hold on
%plot(avgtimes, queueavgmm, '.g')
%plot(avgtimes, queueavgff, 'r')
plot(avgtimes(1:599), queueavgff(1:599), '.r')
%ciplot(queueffconf(:,1), queueffconf(:,2), avgtimes, 'b',0.5);
%plot(avgtimes, setpointavgff, 'r')
%plot(avgtimes(1:599), setpointavgff(1:599), 'k')
%plot(avgtimes, setpointavgff, 'k')
%ciplot(setpointffconf(:,1), setpointffconf(:,2), avgtimes, 'r', 0.5);
%plot(avgtimes, queueavgff, '.r')

axis([0 300 0 100])
hold off;

subplot(3,1,3)
hold on;
plot(avgtimes, 1.0*ones(size(avgtimes)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
%plot(avgtimes, respavgff, 'r')
plot(avgtimes(1:599), respavgff(1:599), 'k')
%ciplot(respffconf(:,1), respffconf(:,2), avgtimes', 'r',0.5);
%plot(avgtimes, respavgff, 'r')
axis([0 300 0 1.5])


hold off;

%% plot normal transients

subplot(3,1,1)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
%plot(times, expdimmersfb, 'b')
%plot(times, v)
plot(times, expdimmersff)
%axis([0 500 -10 10])
hold off

subplot(3,1,2)
hold on
%plot(avgtimes, queueavgmm, '.g')
plot(times, queue_lengthsff)
%plot(avgtimes, setpointavgff, 'r')
plot(times, inner_setpointsff, 'k')
%plot(times, arrivalshat, 'r')
%axis([0 500 0 100])
%plot(avgtimes, queueavgff, '.r')

%axis([0 10000 0 150])
hold off;

subplot(3,1,3)
hold on;
plot(times, 1.0*ones(size(times)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
%plot(times, responsetimesfb, 'b')
plot(times, responsetimesff)
%plot(times, np95_latencies_short, 'r')
axis([0 500 0 2])
%plot(avgtimes, respavgff, 'r')


hold off;

%% Plot real experiments
times = times - times(1);
subplot(3,1,1)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
plot(times, expdimmersreal, 'b')
%axis([1500 1800 0 1])
%plot(avgtimes, expdimmersff(1:600), 'r')
hold off

subplot(3,1,2)
hold on
%plot(avgtimes, queueavgmm, '.g')
plot(times, queue_lengthsreal, '.b')
%plot(avgtimes, setpointavgff, 'r')
plot(times, inner_setpointsreal, '.k')
plot(times, arrivalshat, 'r')
%axis([0 600 0 30])
%plot(avgtimes, queueavgff, '.r')

%axis([0 10000 0 150])
hold off;

subplot(3,1,3)
hold on;
plot(times, 1.0*ones(size(times)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
%plot(times, responsetimesreal, '.b')
plot(times, np95_latencies_long, 'b')
plot(times, np95_latencies_short, 'r')

%axis([1500 1800 0 3])
%plot(avgtimes, respavgff, 'r')


hold off;

%% plot real exp problem
figure()
hold on
plot(times, queue_lengthsreal, 'b')
plot(times, inner_setpointsreal, 'k')
axis([0 6000 0 100])
hold off






