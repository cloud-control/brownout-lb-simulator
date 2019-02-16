%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

READ_NEW = 1;

if READ_NEW
    path = '/home/johanr/Projects/brownout-lb-simulator/result_large_batch';
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 2);
    
    for k = 1:m
        k
        dataCell{k, 1} = read_mcData([path '/' tests(k).name]);
        dataCell{k, 2} = tests(k).name;
    end
    
    save('datafiles/data-large_batch.mat', 'dataCell');
else
    tmp = load('datafiles/data-large_batch.mat');
    dataCell = tmp.dataCell;
end

%% Process data

LAMBDA_FRAC = [0.1, 0.3, 0.5, 0.7];
CLONES = [1, 2, 3, 4, 6, 12]; 
MC_SIMS = 20

m = size(dataCell, 1)

testData = struct(  'testName', [], ...
                    'minAvgRTVal', [], ...
                    'minAvgRTSer', [], ...
                    'minP95RTVal', [], ... 
                    'minP95RTSer', [], ...
                    'minStdRTVal', [], ...
                    'minStdRTSer', [], ...
                    'meanUtils' , [], ...
                    'stdUtils', [], ...
                    'totalReqs', [])
                    
for test = 1:m
    
    if strcmp(dataCell{test, 2}, "RIQ12") || strcmp(dataCell{test, 2}, "IQ12")
       continue 
    end
    
    data = dataCell{test, 1}
    
    % Find the best cloning for each arrival rate frac
    split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
    vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
    rates = sort(unique(cellfun(@(x) str2num(x), vals)));

    lenRate = length(rates);

    minAvgRTVal = zeros(lenRate, MC_SIMS);
    minAvgRTSer = zeros(lenRate, MC_SIMS);
    minP95RTVal = zeros(lenRate, MC_SIMS);
    minP95RTSer = zeros(lenRate, MC_SIMS);
    minStdRTVal = zeros(lenRate, MC_SIMS);
    minStdRTSer = zeros(lenRate, MC_SIMS);

    meanUtils = zeros(lenRate, length(CLONES));
    stdUtils = zeros(lenRate, length(CLONES));

    totalReqs = zeros(MC_SIMS, length(CLONES), lenRate);
    
    for k = 1:lenRate
        rate = rates(k);
        ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));


        disp([num2str(rate) ' ' num2str(size(data(ind, :), 1))])

        % bugcheck
        %if size(data(ind, :), 1) ~= length(CLONES)
        %    error("Wrong number of servers found!")
        %end

        D = data(ind, :);
        [m, ~] = size(D);
        avgRT = zeros(MC_SIMS, m);
        p95RT = zeros(MC_SIMS, m);
        stdRT = zeros(MC_SIMS, m);
        meanUtil = zeros(MC_SIMS, m);
        reqs = zeros(MC_SIMS, m);
        for i = 1:m
            avgRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.avgResponseTime);
            p95RT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.p95ResponseTime);
            stdRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.stddevResponseTime);

            util = [cellfun(@(x) str2num(x), table2cell(D{i,1}(:, 10:end)))];
            meanUtil(:, i) = mean(util, 2);
            
            reqs(:, i) = [cellfun(@(x) str2num(x), D{i, 1}.numRequests)];
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

        meanUtils(k, :) = mean(meanUtil, 1);
        stdUtils(k, :) = std(meanUtil, [], 1);
        totalReqs(:,:,k) = reqs;
    end
    
   tmp_struct = struct(  'testName', dataCell{test, 2}, ...
                    'minAvgRTVal', minAvgRTVal, ...
                    'minAvgRTSer', minAvgRTSer, ...
                    'minP95RTVal', minP95RTVal, ... 
                    'minP95RTSer', minP95RTSer, ...
                    'minStdRTVal', minStdRTVal, ...
                    'minStdRTSer', minStdRTSer, ...
                    'meanUtils' , meanUtils, ...
                    'stdUtils', stdUtils, ...
                    'totalReqs', totalReqs);
    testData = [testData; tmp_struct];
end

%% Analytic results

addpath("opt_clone_funcs")

[optSer, meanRT] = analytic_central_queue(LAMBDA_FRAC, CLONES);

[optSer, meanRT] = analytic_clusterRandom_FCFS(LAMBDA_FRAC, CLONES);

[optSer, meanRT] = analytic_clusterRandom_PS(LAMBDA_FRAC, CLONES);

% DOES NOT EXIST IN IMPLEMENTATION?
[optSer, meanRT] = analytic_clusterRR_FCFS(LAMBDA_FRAC, CLONES);

% Calculate Cluster-JSQ-FCFS, Can we make it better?
[optSer, meanRT] = analytic_clusterJSQ_FCFS(LAMBDA_FRAC, CLONES);
 
% Calculate Cluster-JSQ-PS
[optSer, meanRT] = analytic_clusterJSQ_PS(LAMBDA_FRAC, CLONES);
 

% Implement and run in simulator?
% Cluster-RR-FCFS, using Kingmans formula
% Cluster-RR-PS, no known approximation?

% Both optimal clone amount / expected value RT at that amount

% IQ12, RIQ12 not possible, special
% JSQ-FCFS/PS, Random-FCFS/PS, RR-FCFS/PS not possible since not
%   synchronized


%% Plot optimal servers

sIdx = [2, 3, 4, 5, 6, 1];

n = length(testData)-1
m = length(LAMBDA_FRAC);

figure(1)
clf()
sgtitle("Optimal clone clount")
for k = 1:m
    Y = zeros(n, MC_SIMS);
    X = []
    for i = 1:n
        Y(i, :) = testData(i+1).minAvgRTSer(k, :);
        X = [X, convertCharsToStrings(testData(i+1).testName)];
    end
    [~, idx] = sort(mean(Y, 2));
    Y = Y(idx, :)
    X = X(idx)

    subplot(m, 1, k)
    hold on;
    boxplot(Y', X)
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(k)))
    yticks(CLONES)
    set(gca, 'yscale', 'log')
    ylim([0.8, 15])
end

figure(2)
clf()
sgtitle("Minimal response time over clone set")
for k = 1:m
    Y = zeros(n, MC_SIMS);
    X = []
    for i = 1:n
        Y(i, :) = testData(i+1).minAvgRTVal(k, :);
        X = [X, convertCharsToStrings(testData(i+1).testName)];
    end

    [~, idx] = sort(mean(Y, 2));
    Y = Y(idx, :)
    X = X(idx)
    subplot(m, 1, k)
    hold on;
    boxplot(Y', X)
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(k)))
    %set(gca, 'yscale', 'log')
end
    
    
figure(3)
clf()
sgtitle("Number of request over clone-count")
for i = 1:n
    for k=1:m
        subplot(n, m, k + (i-1)*m)
        reqs = testData(i+1).totalReqs(:,:,k);
        hold on;
        boxplot(reqs(:, sIdx), CLONES)
        title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(k)))
        ylim([0, 1.2*1e6])
        if k == 1
           ylabel(testData(i+1).testName)
        end
    end
end


%% Save to CSV


%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "c")), split);
end
