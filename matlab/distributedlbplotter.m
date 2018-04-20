%% Clear everything and set exp dir
close all;
clear;
clc;

%experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/brownout-lb-simulator//results/trivial/cc/';
%experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/sim-repo-2/brownout-lb-simulator/results/trivial/cc';
experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/icac2018_resultsv2/random-vs-sqf/sqf';


%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
optResponseTimes95th = content(:,2);
%lbweights = content(:,3:7);

%% Get total optional response time data from loadbalancer

lb_file_name2 = [experiment_dir, '/', 'sim-lb-allOpt.csv'];
content2 =  csvread(lb_file_name2);

optContents = content2(:,1);
allOpts = find(optContents == 1);
allResponseTimes = content2(:,2);
allOptResponseTimes = allResponseTimes(allOpts);

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
    servertimes= content(:, 1);
    optServer = content(:,2);
    optServerResponseTimes(:,i) = optServer;
    q = content(:,6);
    queues(:,i) = q;
    
    expdim = content(:,12);
    expdimmers(:,i) = expdim;
end


%% plot normal transients
figure()
hold on;
plot(lbtimes, optResponseTimes95th, 'g')
plot([0 250], [1 1])

%plot(servertimes, optServerResponseTimes, 'r')

%plot(servertimes, queues, 'r')

%%
figure()
subplot(3,1,1)
plot(lbtimes, optResponseTimes95th)
subplot(3,1,2)
plot(lbtimes, lbweights)
subplot(3,1,3)
plot(servertimes, expdimmers)

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











