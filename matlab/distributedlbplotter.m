%% Clear everything and set exp dir
%close all;
clear;
%clc;

%experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/brownout-lb-simulator//results/trivial/cc/';
experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/sim-repo/brownout-lb-simulator/results/trivial/cc';

%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
optResponseTimes = content(:,29);

%% Get total optional response time data from loadbalancer

lb_file_name2 = [experiment_dir, '/', 'sim-lb-tommi.csv'];
content2 =  csvread(lb_file_name2);
allOptResponseTimes = content2(:,1);

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
end


%% plot normal transients
figure()

plot(lbtimes, optResponseTimes)
hold on;
plot(servertimes, optServerResponseTimes(:,1))

%% plot statistically significant transients

figure()

ciplot(respconf(:,1), respconf(:,2), [avgtimes], 'b', 0.5);

hold on;

ciplot(server1respconf(:,1), server1respconf(:,2), [avgtimes], 'r', 0.5);

plot([0 250], [1 1], 'k')

csvVector1dr = [avgtimes, respconf(:,1)];
csvVector2dr = [avgtimes(end:-1:1), respconf(end:-1:1,2)];
csvVectordr = [csvVector1dr; csvVector2dr];
csvwrite('distributed-lb-sqf-response-times.csv',csvVectordr)

csvVector1drs1 = [avgtimes, server1respconf(:,1)];
csvVector2drs1 = [avgtimes(end:-1:1), server1respconf(end:-1:1,2)];
csvVectordrs1 = [csvVector1drs1; csvVector2drs1];
csvwrite('distributed-lb-sqf-server1-response-times.csv',csvVectordrs1)











