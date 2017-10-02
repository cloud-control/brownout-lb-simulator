%% Clear everything
close all;
clear;
clc;

%% Get total response time data of all servers

experiment_dir2 = '/local/home/tommi/CloudControl/SIGMETRICS2018/brownout-lb-simulator//results/trivial/cc-sqf/';
server_files2 = dir([experiment_dir2, '/sim-server*-ctl-tommi.csv']);
num_replicas2 = length(server_files2);

lengths = [0 0 0];

for i = 1:num_replicas2
    filename2 = server_files2(i).name;
    content2 = csvread([experiment_dir2, '/', filename2]);
    lengths(i) = length(content2);
    
   
end

maxlen = max(lengths);

optionalTimes = NaN(maxlen, num_replicas2);

for i = 1:num_replicas2
    filename2 = server_files2(i).name;
    content2 = csvread([experiment_dir2, '/', filename2]);
    
    optTimes = content2(:,1);
    
    if length(optTimes) < maxlen
        nanlen = maxlen-length(optTimes);
        optionalTimes(:,i) = [optTimes;NaN(nanlen,1)];
    else
        optionalTimes(:,i) = optTimes;
    end  
    
end

varOpt = nanvar(optionalTimes)



%% Get simulation data
experiment_dir = '/local/home/tommi/CloudControl/SIGMETRICS2018/brownout-lb-simulator//results/trivial/cc-sqf/';
server_files = dir([experiment_dir, '/sim-server*-ctl.csv']);
num_replicas = length(server_files);

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
    responsetimes(:,i) = resp;
    np95_lat = content(:,3);
    np95_latencies(:, i) = np95_lat;
    np95_lat_long = content(:,4);
    np95_latencies_long(:, i) = np95_lat_long;
    np95_lat_short = content(:,5);
    np95_latencies_short(:, i) = np95_lat_short;
    queue = content(:,6);
    queue_lengths(:,i) = queue;
    avgqueue = content(:,7);
    avgqueue_lengths(:,i) = avgqueue;
    inner = content(:, 8);
    inner_setpoints(:, i) = inner;
    arr = content(:,9);
    arrivals(:,i) = arr;
    arrhat = content(:,10);
    arrivalshat(:,i) = arrhat;
    dim = content(:,11);
    avgdimmers(:,i) = dim;
    expdim = content(:,12);
    expdimmers(:,i) = expdim;
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


%% plot statistically significant transients

k = 2; % the current replica 

l = 2*(k-1) + 1; % index for conf int plots


subplot(4,1,1)
hold on
plot(avgtimes(1:799), expdimmersavg(1:799, k), 'k')
ciplot(expdimconf(:,l), expdimconf(:,(l+1)), avgtimes, 'b',0.5);
axis([0 300 0 1])
hold off

subplot(4,1,2)
hold on
plot(avgtimes(1:799), vavg(1:799, k), 'k')
ciplot(vconf(:,l), vconf(:,(l+1)), avgtimes, 'b',0.5);
axis([0 300 -2 4])
hold off

subplot(4,1,3)
hold on
%plot(avgtimes, queueavgmm, '.g')
%plot(avgtimes, queueavgff, 'r')
%plot(avgtimes(1:799), queueavg(1:799,k), 'k')
%ciplot(queueconf(:,l), queueconf(:,(l+1)), avgtimes, 'b',0.5);
%plot(avgtimes, setpointavgff, 'r')
%plot(avgtimes(1:599), setpointavgff(1:599), 'k')
plot(avgtimes(1:799), setpointavg(1:799,k), 'k')
ciplot(setpointconf(:,l), setpointconf(:,(l+1)), avgtimes, 'r', 0.5);
%plot(avgtimes, queueavgff, '.r')

axis([0 300 35 70])
hold off;

subplot(4,1,4)
hold on;
plot(avgtimes, 1.0*ones(size(avgtimes)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
%plot(avgtimes, respavgff, 'r')
plot(avgtimes(1:799), respavg(1:799,k))
ciplot(respconf(:,l), respconf(:,(l+1)), avgtimes, 'b',0.5);
%plot(avgtimes, respavgff, 'r')
axis([0 300 0 1.5])


hold off;

%% plot normal transients

subplot(3,1,1)
hold on
%plot(avgtimes, expdimmersmm(1:600), 'g')
%plot(times, expdimmersfb, 'b')
%plot(times, v)
plot(times, expdimmers)
%axis([0 500 -10 10])
hold off

subplot(3,1,2)
hold on
%plot(avgtimes, queueavgmm, '.g')
plot(times, queue_lengths)
%plot(avgtimes, setpointavgff, 'r')
plot(times, inner_setpoints, 'k')
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
plot(times, responsetimes)
%plot(times, np95_latencies_short, 'r')
axis([0 500 0 2])
%plot(avgtimes, respavgff, 'r')


hold off;





