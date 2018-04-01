%% Clear everything and set exp dir
close all;
clear;
%clc;

experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/brownout-lb-simulator//results/trivial/co-op/';

%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb-co-op.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
responseTimes = content(:,2:6);
lbserviceTimes = content(:,12);
waitingTimes = content(:,9);
waitingTimes95th = content(:,10);
waitingQueue = content(:,11);
lambdaHat = content(:,13);
queueSetpoints = content(:,14);
optResponseTimes = content(:,15);
waitingTimeSetpoints = content(:,16);
serviceTimeSetpoints = content(:,17);

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
    serviceTime = content(:,2);
    serviceTimes(:,i) = serviceTime;
    filteredServiceTime = content(:,3);
    filteredServiceTimes(:,i) = filteredServiceTime;
    serviceTimeSetpoint = content(:,4);
    serviceTimeSetpoints(:,i) = serviceTimeSetpoint;
    ctrl = content(:,5);
    ctrls(:,i) = ctrl;
    actuatedCtrl = content(:,6);
    actuatedCtrls(:,i) = actuatedCtrl;
    estimatedProcessGain = content(:,7);
    estimatedProcessGains(:,i) = estimatedProcessGain;
end


%% plot normal transients
figure()

subplot(4,1,1)

hold on
plot(lbtimes,ones(size(lbtimes)), 'k')
plot(lbtimes, optResponseTimes)
hold off;

subplot(4,1,2)
plot(lbtimes, queueSetpoints, 'r')
hold on;
plot(lbtimes, waitingQueue, 'b')
%axis([99 149 0 120])

subplot(4,1,3)
%plot(lbtimes,ones(size(lbtimes)), 'k')
hold on
plot(lbtimes, waitingTimes, 'b')
%plot(lbtimes, waitingTimes95th, 'r')
plot(lbtimes, waitingTimeSetpoints, 'k')
%axis([0 20 0 120])

subplot(4,1,4)
%plot(lbtimes,ones(size(lbtimes)), 'k')
hold on
plot(lbtimes, lbserviceTimes, 'b')
%plot(lbtimes, waitingTimes95th, 'r')
plot(lbtimes, serviceTimeSetpoints, 'k')
%axis([0 20 0 120])


figure()

subplot(3,1,1)
plot(servertimes, ctrls(:,1), 'r');
hold on;
plot(servertimes, actuatedCtrls(:,1), 'b');

subplot(3,1,2)
plot(servertimes, serviceTimes(:,1), 'b')
hold on;
plot(servertimes, 0.7*ones(size(servertimes)), 'k')
%axis([0 200 0 0.3])

subplot(3,1,3)
plot(servertimes, estimatedProcessGains(:,1))

%% plot statistically significant transients
close all
subplot(2,1,1)
plot(avgtimes, queueavg, 'r')
ciplot(queueconf(:,1), queueconf(:,2), avgtimes, 'r', 0.5);
hold on;
plot(avgtimes, queuesetpointavg, 'r')
ciplot(queuesetpointconf(:,1), queuesetpointconf(:,2), avgtimes, 'b', 0.5);

subplot(2,1,2)
plot(avgtimes, waitingtimeavg, 'r')
ciplot(waitingtimeconf(:,1), waitingtimeconf(:,2), avgtimes, 'r', 0.5);

% 
% csvVector1 = [avgtimes', queueconf(:,1)];
% csvVector2 = [avgtimes(end:-1:1)', queueconf(end:-1:1,2)];
% csvVector = [csvVector1; csvVector2];
% csvwrite('sim-queues-conf-beta-1.csv',csvVector)
% csvwrite('queue-theory-beta-1.csv', [simulinkqueue.time, simulinkqueue.data])











