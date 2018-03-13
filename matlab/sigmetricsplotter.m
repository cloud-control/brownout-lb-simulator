%% Clear everything and set exp dir
close all;
clear;
%clc;

experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/brownout-lb-simulator//results/trivial/co-op/';

%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb-co-op.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
responseTimes = content(:,2:4);
serviceTimes = content(:,10:12);
waitingTimes = content(:,7);
waitingTimes95th = content(:,8);
waitingQueue = content(:,9);
lambdaHat = content(:,13);
queueSetpoints = content(:,14);


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
    avgServiceTime = content(:,2);
    avgServiceTimes(:,i) = avgServiceTime;
    filteredServiceTime = content(:,3);
    filteredServiceTimes(:,i) = filteredServiceTime;
    serviceTimeSetpoint = content(:,4);
    serviceTimeSetpoints(:,i) = serviceTimeSetpoint;
    ctrl = content(:,5);
    ctrls(:,i) = ctrl;
    actuatedCtrl = content(:,6);
    actuatedCtrls(:,i) = actuatedCtrl;
end


%% plot normal transients
figure()

subplot(3,1,1)

hold on

plot(lbtimes, lambdaHat)
hold off;

subplot(3,1,2)
plot(lbtimes, queueSetpoints, 'r')
hold on;
plot(lbtimes, waitingQueue, 'b')

subplot(3,1,3)
plot(lbtimes,ones(size(lbtimes)), 'k')
hold on
plot(lbtimes, waitingTimes, 'b')
%plot(times, waitingTimes95th, 'r')
%axis([0 20 0 120])


figure()

subplot(2,1,1)
plot(servertimes, ctrls(:,1), 'r');
hold on;
plot(servertimes, actuatedCtrls(:,1), 'b');

subplot(2,1,2)
plot(servertimes, filteredServiceTimes(:,1), 'b')
hold on;
plot(servertimes, 0.2*ones(size(servertimes)), 'k')










