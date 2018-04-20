%% Clear everything and set exp dir
close all;
clear;
clc;

experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/sim-repo/brownout-lb-simulator//results/trivial/co-op/';

%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb-co-op.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
optResponseTimes = content(:,2);
lbserviceTimes = content(:,8);
waitingTimes = content(:,5);
waitingTimes95th = content(:,6);
waitingQueue = content(:,7);
lambdaHat = content(:,9);
queueSetpoints = content(:,10);

waitingTimeSetpoints = content(:,11);
lbserviceTimeSetpoints = content(:,12);
waitingThresholds = content(:,13);

%% Get total waiting time data from loadbalancer

lb_file_name2 = [experiment_dir, '/', 'sim-lb-co-op-tommi.csv'];
content2 =  csvread(lb_file_name2);
allWaitingTimes = content2(:,1);

%% Get simulation data from servers
server_files = dir([experiment_dir, '/sim-server*-ctl.csv']);
num_replicas = length(server_files);

for i = 1:num_replicas
    
    filename = server_files(i).name;
    servercontent = csvread([experiment_dir, '/', filename]);
    
    servertimes= servercontent(:, 1);
    serviceTime = servercontent(:,2);
    serviceTimes(:,i) = serviceTime;
    filteredServiceTime = servercontent(:,4);
    filteredServiceTimes(:,i) = filteredServiceTime;
    serviceTimeSetpoint = servercontent(:,5);
    serviceTimeSetpoints(:,i) = serviceTimeSetpoint;
    ctrl = servercontent(:,6);
    ctrls(:,i) = ctrl;
    actuatedCtrl = servercontent(:,7);
    actuatedCtrls(:,i) = actuatedCtrl;
    estimatedProcessGain = servercontent(:,8);
    estimatedProcessGains(:,i) = estimatedProcessGain;
end


%% plot normal transients
figure()

subplot(4,1,1)

hold on;
%plot(lbtimes, queueSetpoints, 'r')
plot(lbtimes, optResponseTimes, 'b')
hold off;

subplot(4,1,2)
plot(lbtimes, waitingThresholds, 'b')

%axis([99 149 0 120])

subplot(4,1,3)
%plot(lbtimes,ones(size(lbtimes)), 'k')
hold on
plot(lbtimes, waitingTimes, 'b')
%plot(lbtimes, waitingTimes95th, 'r')
%plot(lbtimes, waitingTimeSetpoints, 'k')
%axis([0 20 0 120])

subplot(4,1,4)
%plot(lbtimes,ones(size(lbtimes)), 'k')
hold on
plot(lbtimes, lbserviceTimes, 'b')
%plot(lbtimes, waitingTimes95th, 'r')
plot(lbtimes, lbserviceTimeSetpoints, 'k')
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

%% plot statistically significant transients for service times
%close all
figure()
subplot(3,1,1)
ciplot(estimatedProcessGainsconf(:,1), estimatedProcessGainsconf(:,2), avgtimes, 'r', 0.5);

subplot(3,1,2)
ciplot(ctrlsconf(:,1), ctrlsconf(:,2), avgtimes, 'r', 0.5);
hold on;
ciplot(actuatedCtrlsconf(:,1), actuatedCtrlsconf(:,2), avgtimes, 'b', 0.5);

subplot(3,1,3)
ciplot(serviceTimesconf(:,1), serviceTimesconf(:,2), avgtimes, 'r', 0.5);
hold on;
plot([0 250], [0.5 0.5], 'k')

csvVector1e = [avgtimes, estimatedProcessGainsconf(:,1)];
csvVector2e = [avgtimes(end:-1:1), estimatedProcessGainsconf(end:-1:1,2)];
csvVectore = [csvVector1e; csvVector2e];
csvwrite('service-estimates.csv',csvVectore)

csvVector1u = [avgtimes, ctrlsconf(:,1)];
csvVector2u = [avgtimes(end:-1:1), ctrlsconf(end:-1:1,2)];
csvVectoru = [csvVector1u; csvVector2u];
csvwrite('service-control-signals.csv',csvVectoru)

csvVector1ua= [avgtimes, actuatedCtrlsconf(:,1)];
csvVector2ua = [avgtimes(end:-1:1), actuatedCtrlsconf(end:-1:1,2)];
csvVectorua = [csvVector1ua; csvVector2ua];
csvwrite('service-control-actuated.csv',csvVectorua)

csvVector1st= [avgtimes, serviceTimesconf(:,1)];
csvVector2st = [avgtimes(end:-1:1), serviceTimesconf(end:-1:1,2)];
csvVectorst = [csvVector1st; csvVector2st];
csvwrite('service-times.csv',csvVectorst)


%% plot statistically significant transients for waiting times
%close all
figure()
subplot(3,1,1)
plot(avgtimes, queueavg, 'r')
ciplot(queueconf(:,1), queueconf(:,2), avgtimes, 'r', 0.5);
hold on;
plot(avgtimes, queuesetpointavg, 'r')
ciplot(queuesetpointconf(:,1), queuesetpointconf(:,2), avgtimes, 'b', 0.5);

subplot(3,1,2)
plot(avgtimes, waitingthresholdavg, 'r')
ciplot(waitingthresholdconf(:,1), waitingthresholdconf(:,2), avgtimes, 'r', 0.5);
hold on;

subplot(3,1,3)
plot(avgtimes, waitingtimeavg, 'r')
ciplot(waitingtimeconf(:,1), waitingtimeconf(:,2), avgtimes, 'r', 0.5);
hold on;
plot([0 250], [1 1], 'k')


% csvVector1q = [avgtimes, queueconf(:,1)];
% csvVector2q = [avgtimes(end:-1:1), queueconf(end:-1:1,2)];
% csvVectorq = [csvVector1q; csvVector2q];
% csvwrite('waiting-threshold-queues.csv',csvVectorq)
% 
% csvVector1wt = [avgtimes, waitingtimeconf(:,1)];
% csvVector2wt = [avgtimes(end:-1:1), waitingtimeconf(end:-1:1,2)];
% csvVectorwt = [csvVector1wt; csvVector2wt];
% csvwrite('waiting-threshold-waiting-times.csv',csvVectorwt)
% 
% csvVector1thres = [avgtimes, waitingthresholdconf(:,1)];
% csvVector2thres = [avgtimes(end:-1:1), waitingthresholdconf(end:-1:1,2)];
% csvVectorthres = [csvVector1thres; csvVector2thres];
% csvwrite('waiting-threshold-waiting-thresholds.csv',csvVectorthres)














