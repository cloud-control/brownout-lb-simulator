%% Clear everything and set exp dir
close all;
clear;
clc;

experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/icac2018-results-v3/co-op-50-selected';
%experiment_dir = '/local/home/tommi/CloudControl/ICAC2018/sim-repo-2/brownout-lb-simulator//results/trivial/co-op/';

%% Get data from distributed files

lb_file_name = [experiment_dir, '/', 'sim-lb.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
optResponseTimes95th = content(:,2);

lb_file_name2 = [experiment_dir, '/', 'sim-lb-allOpt.csv'];
content2 =  csvread(lb_file_name2);

optContents = content2(:,1);
allOpts = find(optContents == 1);
allResponseTimes = content2(:,2);
allOptResponseTimes = allResponseTimes(allOpts);
allOptResponseTimes = allOptResponseTimes(allOptResponseTimes > 0.0);

%% Get data from Co-Op files

lb_file_name = [experiment_dir, '/', 'sim-lb-co-op.csv'];
content =  csvread(lb_file_name);

lbtimes = content(:,1);
optResponseTimes95th = content(:,3);

lb_file_name2 = [experiment_dir, '/', 'sim-lb-co-op-allOpt.csv'];
content2 =  csvread(lb_file_name2);

optContents = content2(:,1);
allOpts = find(optContents == 1);
allResponseTimes = content2(:,2);
allOptResponseTimes = allResponseTimes(allOpts);
allOptResponseTimes = allOptResponseTimes(allOptResponseTimes > 0.0);

%% CDF plotting
close all;
cdfplot(allOptResponseTimes);
h = gcf;
axesObjs = get(h, 'Children');  %axes handles
dataObjs = get(axesObjs, 'Children'); %handles to low-level graphics objects in axes
objTypes = get(dataObjs, 'Type');  %type of low-level graphics object
xdata = get(dataObjs, 'XData');  %data from low-level grahics objects
ydata = get(dataObjs, 'YData');

fbcdfx = xdata(2:100:end-1);
fbcdfx = [fbcdfx xdata(end-1)];
fbcdfy = ydata(2:100:end-1);
fbcdfy = [fbcdfy ydata(end-1)];
close all;
figure()
plot(fbcdfx,fbcdfy, 'b');
hold on
% plot(fbcdfx2,fbcdfy2, 'r');
% plot(fbcdfx3,fbcdfy3, 'g');
% plot(fbcdfx4,fbcdfy4, 'k');
% plot(fbcdfx5,fbcdfy5, 'y');
axis([0 3 -0.1 1.1])

csvVectorcdf = [fbcdfx', fbcdfy'];
csvwrite('randomized-co-op-50-cdf.csv',csvVectorcdf)

 save('randomized-co-op-50.mat')

%% Get stats
samplePeriod = 0.25;
IAE = samplePeriod*sum(abs(optResponseTimes95th - 1))
SD = std(allOptResponseTimes)
maxResp = max(allOptResponseTimes)

%% Plot selected scenarios

figure()

%ciplot(respconf(:,1), respconf(:,2), [avgtimes], 'b', 0.5);
plot(avgtimes, optResponseTimes95thavg, 'b')
hold on;

ciplot(optResponseTimes95thconf(:,1), optResponseTimes95thconf(:,2), [avgtimes], 'r', 0.5);

plot([0 250], [1 1], 'k')

csvVectordr = [avgtimes, optResponseTimes95thavg];
csvwrite('selected-co-op-50-response-times-avg.csv',csvVectordr)

csvVector1r = [avgtimes, optResponseTimes95thconf(:,1)];
csvVector2r = [avgtimes(end:-1:1), optResponseTimes95thconf(end:-1:1,2)];
csvVectorr = [csvVector1r; csvVector2r];
csvwrite('selected-co-op-50-response-times.csv',csvVectorr)

save('selected-co-op-50.mat')


