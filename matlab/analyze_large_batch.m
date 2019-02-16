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

m = size(dataCell, 1);

testData = struct(  'testName', [], ...
                    'minAvgRTVal', [], ...
                    'minAvgRTSer', [], ...
                    'minP95RTVal', [], ... 
                    'minP95RTSer', [], ...
                    'minStdRTVal', [], ...
                    'minStdRTSer', [], ...
                    'meanUtils' , [], ...
                    'stdUtils', [], ...
                    'totalReqs', []);

testData_RIQ = struct(  'testName', [], ...
                        'avgRTVal', [], ...
                        'p95RTVal', [], ... 
                        'stdRTVal', [], ...
                        'meanUtils' , [], ...
                        'stdUtils', [], ...
                        'totalReqs', []);
                    
for test = 1:m
       
    data = dataCell{test, 1};
    
    % Find the best cloning for each arrival rate frac
    split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
    vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
    rates = sort(unique(cellfun(@(x) str2num(x), vals)));

    lenRate = length(rates);
    
    
    % Special case if IQ/RIQ, since we do not have different cloning
    % amounts
    if strcmp(dataCell{test, 2}, "RIQ12") || strcmp(dataCell{test, 2}, "IQ12")
        avgRTVal = zeros(lenRate, MC_SIMS);
        p95RTVal = zeros(lenRate, MC_SIMS);
        stdRTVal = zeros(lenRate, MC_SIMS);
        meanUtils = zeros(lenRate, 1);
        stdUtils = zeros(lenRate, 1);

        totalReqs = zeros(MC_SIMS, 1, lenRate);
       
        for k = 1:lenRate
            rate = rates(k);
            ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
            D = data(ind, :);

            avgRTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.avgResponseTime);
            p95RTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.p95ResponseTime);
            stdRTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.stddevResponseTime);
            meanUtils(k, :) = mean(mean([cellfun(@(x) str2num(x), table2cell(D{1,1}(:, 10:end)))], 2));
            stdUtils(k, :) = std(mean([cellfun(@(x) str2num(x), table2cell(D{1,1}(:, 10:end)))], 2));
            totalReqs(:,:,k) = [cellfun(@(x) str2num(x), D{1, 1}.numRequests)];
        end

       tmp_struct = struct(  'testName', dataCell{test, 2}, ...
                        'avgRTVal', avgRTVal, ...
                        'p95RTVal', p95RTVal, ... 
                        'stdRTVal', stdRTVal, ...
                        'meanUtils' , meanUtils, ...
                        'stdUtils', stdUtils, ...
                        'totalReqs', totalReqs);
        testData_RIQ = [testData_RIQ; tmp_struct];
        continue 
    end
    
    % Normal case

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

%% Calculate analytic results and plot results

addpath("opt_clone_funcs")

analytic_optClone = containers.Map();
analytic_meanRT = containers.Map();

[optClone, meanRT] = analytic_central_queue(LAMBDA_FRAC, CLONES);
analytic_optClone('central-queue') = optClone;
analytic_meanRT('central-queue') = meanRT;

[optClone, meanRT] = analytic_clusterRandom_FCFS(LAMBDA_FRAC, CLONES);
analytic_optClone('clusterRandom-FCFS') = optClone;
analytic_meanRT('clusterRandom-FCFS') = meanRT;

[optClone, meanRT] = analytic_clusterRandom_PS(LAMBDA_FRAC, CLONES);
analytic_optClone('clusterRandom-PS') = optClone;
analytic_meanRT('clusterRandom-PS') = meanRT;

% DOES NOT EXIST IN IMPLEMENTATION?
[optClone, meanRT] = analytic_clusterRR_FCFS(LAMBDA_FRAC, CLONES);

% Calculate Cluster-JSQ-FCFS, Can we make it better?
[optClone, meanRT] = analytic_clusterJSQ_FCFS(LAMBDA_FRAC, CLONES);
analytic_optClone('clusterJSQ-FCFS') = optClone;
analytic_meanRT('clusterJSQ-FCFS') = meanRT;
 
% Calculate Cluster-JSQ-PS
[optClone, meanRT] = analytic_clusterJSQ_PS(LAMBDA_FRAC, CLONES);
analytic_optClone('clusterJSQ-PS') = optClone;
analytic_meanRT('clusterJSQ-PS') = meanRT;
 

% Implement and run in simulator?
% Cluster-RR-FCFS, using Kingmans formula
% Cluster-RR-PS, no known approximation?

% Both optimal clone amount / expected value RT at that amount

% IQ12, RIQ12 not possible, special
% JSQ-FCFS/PS, Random-FCFS/PS, RR-FCFS/PS not possible since not
%   synchronized

sIdx = [2, 3, 4, 5, 6, 1];

n = length(testData)-1
m = length(LAMBDA_FRAC);

figure(1)
clf()
sgtitle("Optimal clone clount")
for k = 1:m
    Y = zeros(n, MC_SIMS);
    X = []
    
    Y_theory = [];
    X_theory = [];
    for i = 1:n
        Y(i, :) = testData(i+1).minAvgRTSer(k, :);
        X = [X, convertCharsToStrings(testData(i+1).testName)];
        
        if ~isempty(intersect(analytic_optClone.keys(), testData(i+1).testName))
            optClone = analytic_optClone(testData(i+1).testName)
            Y_theory = [Y_theory, optClone(k)];
            X_theory = [X_theory, i];
        else
           X_theory = [X_theory, 0];
           Y_theory = [Y_theory, 0];
        end
        
    end
    [~, idx] = sort(mean(Y, 2));
    Y = Y(idx, :)
    X = X(idx)
    
    Y_theory = Y_theory(idx);
    %X_theory = X_theory(idx);

    subplot(m, 1, k)
    hold on;
    boxplot(Y', X)
    plot(1:11, Y_theory, 'go')
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
    Y_theory = [];
    X_theory = [];
    
    for i = 1:n
        Y(i, :) = testData(i+1).minAvgRTVal(k, :);
        X = [X, convertCharsToStrings(testData(i+1).testName)];
        
        if ~isempty(intersect(analytic_meanRT.keys(), testData(i+1).testName))
            meanRT = analytic_meanRT(testData(i+1).testName)
            Y_theory = [Y_theory, meanRT(k)];
            X_theory = [X_theory, i];
        else
           X_theory = [X_theory, 0];
           Y_theory = [Y_theory, 0];
        end
        
    end

    [~, idx] = sort(mean(Y, 2));
    Y = Y(idx, :)
    X = X(idx)
    
    Y_theory = Y_theory(idx);
    %X_theory = X_theory(idx);
    
    
    subplot(m, 1, k)
    hold on;
    boxplot(Y', X)
    plot(1:11, Y_theory, 'go')
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(k)))
    %set(gca, 'yscale', 'log')
end


%% Plot amount of requests
    
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


%% Compare IQ/RIQ

m = length(testData_RIQ);

avgRT1 = mean(testData_RIQ(2).avgRTVal, 2);
avgRT2 = mean(testData_RIQ(3).avgRTVal, 2);
avgRT_bounds1 = 2.09 * std(testData_RIQ(2).avgRTVal, [], 2) / sqrt(20);
avgRT_bounds2 = 2.09 * std(testData_RIQ(2).avgRTVal, [], 2) / sqrt(20);

p95RT1 = mean(testData_RIQ(2).p95RTVal, 2);
p95RT2 = mean(testData_RIQ(3).p95RTVal, 2);
p95RT_bounds1 = 2.09 * std(testData_RIQ(2).p95RTVal, [], 2) / sqrt(20);
p95RT_bounds2 = 2.09 * std(testData_RIQ(2).p95RTVal, [], 2) / sqrt(20);

stdRT1 = mean(testData_RIQ(2).stdRTVal, 2);
stdRT2 = mean(testData_RIQ(3).stdRTVal, 2);
stdRT_bounds1 = 2.09 * std(testData_RIQ(2).stdRTVal, [], 2) / sqrt(20);
stdRT_bounds2 = 2.09 * std(testData_RIQ(2).stdRTVal, [], 2) / sqrt(20);

figure(4)
clf()
sgtitle("Comparasion between IQ and RIQ")
subplot(3, 1, 1)
title("Average Response Time")
hold on;
plot(LAMBDA_FRAC, avgRT1, 'b');
plot(LAMBDA_FRAC, avgRT2, 'r');
plot(LAMBDA_FRAC, avgRT1 + avgRT_bounds1, 'b--')
plot(LAMBDA_FRAC, avgRT1 - avgRT_bounds1, 'b--')
plot(LAMBDA_FRAC, avgRT2 + avgRT_bounds2, 'r--')
plot(LAMBDA_FRAC, avgRT2 - avgRT_bounds2, 'r--')
legend(testData_RIQ(2).testName, testData_RIQ(3).testName, 'location', 'northwest')

subplot(3, 1, 2)
title("p95 Response Time")
hold on;
plot(LAMBDA_FRAC, p95RT1, 'b');
plot(LAMBDA_FRAC, p95RT2, 'r');
plot(LAMBDA_FRAC, p95RT1 + p95RT_bounds1, 'b--')
plot(LAMBDA_FRAC, p95RT1 - p95RT_bounds1, 'b--')
plot(LAMBDA_FRAC, p95RT2 + p95RT_bounds2, 'r--')
plot(LAMBDA_FRAC, p95RT2 - p95RT_bounds2, 'r--')
legend(testData_RIQ(2).testName, testData_RIQ(3).testName, 'location', 'northwest')

subplot(3, 1, 3)
title("Std Response Time")
hold on;
plot(LAMBDA_FRAC, stdRT1, 'b');
plot(LAMBDA_FRAC, stdRT2, 'r');
plot(LAMBDA_FRAC, stdRT1 + stdRT_bounds1, 'b--')
plot(LAMBDA_FRAC, stdRT1 - stdRT_bounds1, 'b--')
plot(LAMBDA_FRAC, stdRT2 + stdRT_bounds2, 'r--')
plot(LAMBDA_FRAC, stdRT2 - stdRT_bounds2, 'r--')
legend(testData_RIQ(2).testName, testData_RIQ(3).testName, 'location', 'northwest')


%% Save to CSV


%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "c")), split);
end
