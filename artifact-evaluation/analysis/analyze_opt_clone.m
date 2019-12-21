%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

clc;
clear all;

addpath('./functions')

if ~isfile('clone_to_all.mat')
    path = '../simulation-results/clone-to-all';
    data = read_mcData(path);
    save('clone_to_all.mat', 'data');
else
    tmp = load('clone_to_all.mat');
    data = tmp.data;
end


%% Process data

NBR_OF_DIFF_SERVERS = 12;
MC_SIMS = 20

% Find the best cloning for each arrival rate frac

split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
rates = sort(unique(cellfun(@(x) str2num(x), vals)));

lenRate = length(rates)

minAvgRTVal = zeros(lenRate, MC_SIMS);
minAvgRTSer = zeros(lenRate, MC_SIMS);

minP95RTVal = zeros(lenRate, MC_SIMS);
minP95RTSer = zeros(lenRate, MC_SIMS);

minStdRTVal = zeros(lenRate, MC_SIMS);
minStdRTSer = zeros(lenRate, MC_SIMS);

meanUtils = cell(lenRate, 1);

for k = 1:lenRate
    rate = rates(k);
    ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
    
    disp([num2str(rate) ' ' num2str(size(data(ind, :), 1))])
    
    D = data(ind, :);
    [m, ~] = size(D);
    avgRT = zeros(MC_SIMS, m);
    p95RT = zeros(MC_SIMS, m);
    stdRT = zeros(MC_SIMS, m);
    utils = zeros(MC_SIMS, m);
    for i = 1:m
        avgRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.avgResponseTime);
        p95RT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.p95ResponseTime);
        stdRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.stddevResponseTime);
        
        util = [cellfun(@(x) str2num(x), table2cell(D{i,1}(:, 10:end)))];
        % bugcheck
        for j = 1:MC_SIMS
           if length(unique(util(j, :))) ~= 1
              error("Untilizations are not identical for servers!") 
           end
        end
        utils(:, i) = util(:, 1);
    end
    
    [avg_val, avg_idx] = min(avgRT, [], 2);
    [p95_val, p95_idx] = min(p95RT, [], 2);
    [std_val, std_idx] = min(stdRT, [], 2);

    minAvgRTVal(k, :) = avg_val;
    minAvgRTSer(k, :) = getServerIdx(D, avg_idx);
    minP95RTVal(k, :) = p95_val;
    minP95RTSer(k, :) = getServerIdx(D, p95_idx);
    minStdRTVal(k, :) = std_val;
    minStdRTSer(k, :) = getServerIdx(D, std_idx);
    
    meanUtils{k} = mean(utils,1);
end

%% Get confidence intervals
optclone_conf = zeros(66,2);
optmean_conf = zeros(66,2);

for i=1:66
    optclone_conf(i, :) = confint(minAvgRTSer(i, :));
    optmean_conf(i, :) = confint(minAvgRTVal(i, :));
end

U = rates*0.01 + 0.05;

csvVector1clone = [U, optclone_conf(:,1)];
csvVector2clone = [U(end:-1:1), optclone_conf(end:-1:1,2)];
csvVectorclone = [csvVector1clone; csvVector2clone];
csvwrite('../plots/data/clone-to-all/optclone-confint.csv',csvVectorclone)

csvVector1mean = [U, optmean_conf(:,1)];
csvVector2mean = [U(end:-1:1), optmean_conf(end:-1:1,2)];
csvVectormean = [csvVector1mean; csvVector2mean];
csvwrite('../plots/data/clone-to-all/optmean-confint.csv',csvVectormean)

%% Get theoretical values
clc;
dollycdf = zeros(12, 1);

dollypdf = zeros(12,1);
dollypdf(1) = 0.230; dollypdf(2) = 0.140; dollypdf(3) = 0.09;
dollypdf(4) = 0.03; dollypdf(5) = 0.08; dollypdf(6) = 0.10;
dollypdf(7) = 0.04; dollypdf(8) = 0.140; dollypdf(9) = 0.12;
dollypdf(10) = 0.021; dollypdf(11) = 0.007; dollypdf(12) = 0.002;


dollycdf(1) = 0.230;dollycdf(2) = 0.370;dollycdf(3) = 0.460;
dollycdf(4) = 0.490;dollycdf(5) = 0.570;dollycdf(6) = 0.670;
dollycdf(7) = 0.710;dollycdf(8) = 0.850;dollycdf(9) = 0.970;
dollycdf(10) = 0.991;dollycdf(11) = 0.998;dollycdf(12) = 1.000;

hypermeanservicetime = 1/4.7;
hypercoeff = 10;
arrivalcoeff = 1;

rates = 0.0:0.00001:0.70;

optclones = ones(size(rates));
mus = ones(12,1);
meanRTs = NaN(size(rates));

index = 0;

utils = zeros(length(rates), 12);

minavgresps = -1*ones(1,12);

for lambda = rates
    
minmeans = zeros(1,50);
%minavgresps = -1*ones(1,50);

index = index + 1;
clones = 1:12;
for j = clones
nbrClones = j;
mindollycdf = 1 - (1 - dollycdf).^nbrClones;

cloneminmean = cumsum(1-[0;mindollycdf]);
minmeans(j) = cloneminmean(end);

avgservicetime = hypermeanservicetime* cloneminmean(end);
avgservicerate = 1/avgservicetime;
util = lambda*avgservicetime*j;
mus(j) = avgservicerate;

if util < 1
    utils(index, j) = util;
    minavgresps(j) = 1./((1./avgservicetime) - (lambda*j));
end

end

minresp = min(minavgresps(minavgresps>0));

bestCloningMG1 = find(minavgresps == minresp);
shortestResponseTime = minresp;

optclones(index) = bestCloningMG1;
meanRTs(index) = shortestResponseTime;

end

prev_y = 0.0;

orig_meanRTs = [rates', meanRTs'];

new_index = 1;

new_meanRTs(1, 1) = orig_meanRTs(1, 1);
new_meanRTs(1, 2) = orig_meanRTs(1, 2);

for i = 2:(length(orig_meanRTs(:,2))-1)
    x_val = orig_meanRTs(i,1);
    y_val = orig_meanRTs(i,2);
    
    if (y_val-prev_y) > 0.01
        new_meanRTs(new_index, 1) = x_val;
        new_meanRTs(new_index, 2) = y_val;
        new_index = new_index + 1;
        prev_y = y_val;
    end
end

new_meanRTs(new_index, 1) = orig_meanRTs(end, 1);
new_meanRTs(new_index, 2) = orig_meanRTs(end, 2);

orig_optclones = [rates', optclones'];

prev_y = orig_optclones(1,2);

new_index = 1;

new_optclones(1, 1) = orig_optclones(1, 1);
new_optclones(1, 2) = orig_optclones(1, 2);

for i = 2:(length(orig_optclones(:,2))-1)
    x_val = orig_optclones(i,1);
    y_val = orig_optclones(i,2);
    
    if (y_val-prev_y) < -0.5
        x_val_prev = orig_optclones(i-1,1);
        y_val_prev = orig_optclones(i-1,2);
        new_optclones(new_index, 1) = x_val_prev;
        new_optclones(new_index, 2) = y_val_prev;
        new_index = new_index + 1;
        new_optclones(new_index, 1) = x_val;
        new_optclones(new_index, 2) = y_val;
        new_index = new_index + 1;
        prev_y = y_val;
    end
end

new_optclones(new_index, 1) = orig_optclones(end, 1);
new_optclones(new_index, 2) = orig_optclones(end, 2);

%% Write data to csv

csvwrite('../plots/data/clone-to-all/optclones-ps.csv',new_optclones)
csvwrite('../plots/data/clone-to-all/meanRTs-ps.csv',new_meanRTs)

%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "s")), split);
end
