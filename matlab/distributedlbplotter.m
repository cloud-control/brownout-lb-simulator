%% Clear everything and set exp dir
%close all;
clear;
clc;

experiment_dir = '/local/home/tommi/CloudControl/cloning/brownout-lb-simulator//results/trivial/static/';
%experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/sim-repo-2/brownout-lb-simulator/results/trivial/cc';


%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
lbavgresps = content(:,2);
lbpropoffsets = content(:,3:4);
lbthetahat = content(:,5);
lbmumax = content(:,6);
% lbqueues = content(:,2);
% serverUtils = content(:,4:5);
% queueOffsets = content(:,6:7);
% fbmeas = content(:,8:9);
% serverqueues = content(:,10:11);
% optResponseTimes95th = content(:,3);
% 
% lbweights = content(:,28:33);

%% Get total optional response time data from loadbalancer

lb_file_name2 = [experiment_dir, '/', 'sim-lb-allOpt.csv'];
content2 =  csvread(lb_file_name2);

optContents = content2(:,1);
serverIndex = content2(:,3);
allOpts = find(optContents == 1);
server1 = find(serverIndex == 0);
server2 = find(serverIndex == 1);
server3 = find(serverIndex == 2);
server4 = find(serverIndex == 3);
allResponseTimes = content2(:,2);
allOptResponseTimes = allResponseTimes(allOpts);

nbrServers = 4;

respLen = length(allResponseTimes);

sResp = NaN*ones(respLen, nbrServers);
for i=0:nbrServers-1
    
serverResp = allResponseTimes(serverIndex == i);

for j = 1:length(serverResp)
    sResp(j,i+1) = serverResp(j);
end

end

%% Get total waiting time data from loadbalancer

lb_file_name2 = [experiment_dir, '/', 'sim-lb-allOpt.csv'];
content2 =  csvread(lb_file_name2);

optContents = content2(:,1);
allOpts = find(optContents == 1);
allResponseTimes = content2(:,2);
allOptResponseTimes = allResponseTimes(allOpts);
%% Get simulation data from servers 1
server_files = dir([experiment_dir, '/sim-server*-report.csv']);
num_replicas = length(server_files);

serverqueues = zeros(3001,num_replicas);


for i = 1:num_replicas
    filename = server_files(i).name;
    content = csvread([experiment_dir, '/', filename]);
    size(content)
    
    %util = content(:,4);
    %serverutils(:,i) = util;
    q = content(:,5);

    serverqueues(:,i) = q;
end


%% Get simulation data from servers 2
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
    servertimes= content(:, 1);
    optServer = content(:,2);
    optServerResponseTimes(:,i) = optServer;
    q = content(:,6);
    queues(:,i) = q;
    qs = content(:,8);
    queueSetpoints(:,i) = qs;
    
    arr = content(:,10);
    arrivals(:,i) = arr;
    
    expdim = content(:,12);
    expdimmers(:,i) = expdim;
    
    vhat = content(:,17);
    v(:,i) = vhat;
end


%% plot normal transients
figure()
hold on;
plot(lbtimes, optResponseTimes95th)
%plot([0 250], [1 1])

%plot(servertimes, optServerResponseTimes(:,1), 'r')

%plot(servertimes, queues, 'r')

%%
figure()
subplot(4,1,1)
plot(servertimes, optServerResponseTimes(:,:))
subplot(4,1,2)
plot(servertimes, queueSetpoints(:,:))
subplot(4,1,3)
plot(servertimes, queues(:,:))
subplot(4,1,4)
plot(servertimes, v(:,:))
xlim([0 200])
ylim([-5 5])

%% plot statistically significant transients

figure()

%ciplot(respconf(:,1), respconf(:,2), [avgtimes], 'b', 0.5);

hold on;

ciplot(server1respconf(:,1), server1respconf(:,2), [avgtimes], 'r', 0.5);

plot([0 100], [1 1], 'k')

% csvVector1dr = [avgtimes, respconf(:,1)];
% csvVector2dr = [avgtimes(end:-1:1), respconf(end:-1:1,2)];
% csvVectordr = [csvVector1dr; csvVector2dr];
% csvwrite('distributed-lb-sqf-response-times.csv',csvVectordr)
% 
csvVector1r = [avgtimes, server1respconf(:,1)];
csvVector2r = [avgtimes(end:-1:1), server1respconf(end:-1:1,2)];
csvVectorr = [csvVector1r; csvVector2r];
csvwrite('distributed-lb-sqf-server1-response-times.csv',csvVectorr)











