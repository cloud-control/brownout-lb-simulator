%% Clear everything and set exp dir
close all;
clear;
%clc;

experiment_dir = '/local/home/tommi/CloudControl/SIGMETRICS2018/seminar/brownout-lb-simulator//results/trivial/cc/';

%% Get total response time data of all servers

server_files2 = dir([experiment_dir, '/sim-server*-ctl-tommi.csv']);
num_replicas2 = length(server_files2);

lengths = [0 0 0];

for i = 1:num_replicas2
    filename2 = server_files2(i).name;
    content2 = csvread([experiment_dir, '/', filename2]);
    lengths(i) = length(content2);
    
   
end

maxlen = max(lengths);

optionalTimes = NaN(maxlen, num_replicas2);

for i = 1:num_replicas2
    filename2 = server_files2(i).name;
    content2 = csvread([experiment_dir, '/', filename2]);
    
    optTimes = content2(:,1);
    
    if length(optTimes) < maxlen
        nanlen = maxlen-length(optTimes);
        optionalTimes(:,i) = [optTimes;NaN(nanlen,1)];
    else
        optionalTimes(:,i) = optTimes;
    end  
    
end

stdOpt = nanstd(optionalTimes(1000:end,:))
meanstdOpt = mean(stdOpt)

%% Get simulation data from servers
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
    adapgain = content(:,19);
    adaptiveGain(:,i) = adapgain;
    
end

meanOptT95 = mean(nanmean(responsetimes))
stdOptT95 = nanstd(responsetimes(200:end,:))
meanStdOptT95 = mean(stdOptT95)
meanQueues = mean(queue_lengths(200:end, :))
varQueues = var(queue_lengths(200:end, :))

% %% Get simulation data from loadbalancer
% lb_file = dir([experiment_dir, '/sim-lb.csv']);
% num_replicas = 6;
% filename = lb_file.name;
% content = csvread([experiment_dir, '/', filename]);
% 
% lb_times= content(:, 1);
% 
% for i = 1:num_replicas
% 
%     %getting data   
%     w = content(:,i+1);
%     weights(:,i) = w;
%     
% end
% 
% 
% %% plot statistically significant transients for all replicas
% 
% nbrReplicas = length(lengths);
% 
% 
% figure();
% 
% for k=1:nbrReplicas
%     l = 2*(k-1) + 1; % index for conf int plots
%     
%     if k == 1
%         color = 'b';
%     elseif k == 2
%         color = 'r';
%     elseif k == 3
%         color = 'g';
%     end
% 
%     subplot(4,1,1)
%     hold on
%     plot(avgtimes(1:799), expdimmersavg(1:799, k), color)
%     ciplot(expdimconf(:,l), expdimconf(:,(l+1)), avgtimes, color,0.5);
%     axis([0 300 0 1])
%     hold off
% 
%     subplot(4,1,2)
%     hold on
%     plot(avgtimes(1:799), vavg(1:799, k), color)
%     ciplot(vconf(:,l), vconf(:,(l+1)), avgtimes, color,0.5);
%     axis([0 300 -20 20])
%     hold off
% 
%     subplot(4,1,3)
%     hold on
%     plot(avgtimes(1:799), queueavg(1:799,k), color)
%     ciplot(queueconf(:,l), queueconf(:,(l+1)), avgtimes, color,0.5);
%     %plot(avgtimes(1:799), setpointavg(1:799,k), 'k')
%     %ciplot(setpointconf(:,l), setpointconf(:,(l+1)), avgtimes, 'r', 0.5);
% 
%     axis([0 300 30 60])
%     hold off;
% 
%     subplot(4,1,4)
%     hold on;
%     plot(avgtimes, 1.0*ones(size(avgtimes)), 'k', 'LineWidth', 2.0)
%     plot(avgtimes(1:799), respavg(1:799,k), color)
%     ciplot(respconf(:,l), respconf(:,(l+1)), avgtimes, color,0.5);
%     axis([0 300 0 1.5])
% 
%     hold off;
%     
% end

%% plot normal transients
figure()
% subplot(3,1,1)
% hold on
% %plot(avgtimes, expdimmersmm(1:600), 'g')
% plot(times, arrivalshat(:,1), 'r')
% %plot(times, v)
% %plot(times, adaptiveGain(:,1), 'k')
% %plot(lb_times, weights)
% %axis([0 500 -10 10])
% hold off

subplot(2,1,1)
hold on
%plot(avgtimes, queueavgmm, '.g')
%plot(times, inner_setpoints)
%plot(times, queue_lengths(:,1), 'r')
%plot(times, inner_setpoints(:,1), 'k')
plot(times, adaptiveGain(:,1), 'k')
%plot(times, arrivals(:, 1), 'k')
%plot(times, arrivalshat, 'r')
%axis([0 200 0 100])
%plot(avgtimes, queueavgff, '.r')

%axis([0 10000 0 150])
hold off;

subplot(2,1,2)
hold on;
plot(times, 1.0*ones(size(times)), 'k', 'LineWidth', 2.0)
%plot(avgtimes, respavgmm, 'g')
%plot(times, responsetimesfb, 'b')
plot(times, responsetimes(:,1), 'r')
%plot(times, np95_latencies_short, 'r')
%axis([0 200 0 2])
%plot(avgtimes, respavgff, 'r')
hold off;

figure()
plot(times, 2.*arrivals(:,1), 'rx')



%% SQF test plotting

x = [1 100];
y1 = [60 60];
y2 = [40 40];
m = [50 50];

plot(x,y1, 'b')
hold on;
plot(x,y2, 'r');
plot(x,m, 'k--');







