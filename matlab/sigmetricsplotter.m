%% Clear everything and set exp dir
close all;
clear;
%clc;

experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/brownout-lb-simulator//results/trivial/co-op/';

%% Get data from loadbalancer
lb_file_name = [experiment_dir, '/', 'sim-lb-co-op.csv'];
content =  csvread(lb_file_name);

times = content(:,1);
responseTimes = content(:,2:4);
serviceTimes = content(:,8:10);
waitingTimes = content(:,7);


%% plot normal transients
figure()

subplot(3,1,1)
hold on

plot(times, responseTimes)
axis([0 100 0 1.2])
hold off;

subplot(3,1,2)
plot(times, waitingTimes)

subplot(3,1,3)
plot(times, serviceTimes)









