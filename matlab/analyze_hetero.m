%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

READ_NEW = 1;

if READ_NEW
    path = '/home/johanr/Projects/brownout-lb-simulator/result_hetero';
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 2);
    
    for k = 1:m
        k
        dataCell{k, 1} = read_mcData([path '/' tests(k).name]);
        dataCell{k, 2} = tests(k).name;
    end
    
    save('datafiles/data-hetero.mat', 'dataCell');
else
    tmp = load('datafiles/data-hetero.mat');
    dataCell = tmp.dataCell;
end

%% Process data

LAMBDA_FRAC = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];
MC_SIMS = 20;

m = size(dataCell, 1);

testData= struct(  'testName', [], ...
                    'avgRTVal', [], ...                
                    'p95RTVal', [], ... 
                    'stdRTVal', [], ...
                    'meanUtils' , [], ...
                    'totalReqs', []);
                    
for test = 1:m
       
    data = dataCell{test, 1};
    
    % Find the best cloning for each arrival rate frac
    split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
    vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
    rates = sort(unique(cellfun(@(x) str2num(x), vals)));

    lenRate = length(rates);
    
    avgRTVal = zeros(lenRate, MC_SIMS);
    p95RTVal = zeros(lenRate, MC_SIMS);
    stdRTVal = zeros(lenRate, MC_SIMS);

    meanUtils = zeros(lenRate, MC_SIMS);
    totalReqs = zeros(lenRate, MC_SIMS);
    
    for k = 1:lenRate
        rate = rates(k);
        ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
        disp([num2str(rate) ' ' num2str(size(data(ind, :), 1))])
    
        if sum(ind) ~= 1
            error("Set of indexes is not 1!")
        end
        
        D = data(ind, :);
        avgRTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.avgResponseTime);
        p95RTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.p95ResponseTime);
        stdRTVal(k, :) = cellfun(@(x) str2num(x), D{1, 1}.stddevResponseTime);

        util = [cellfun(@(x) str2num(x), table2cell(D{1,1}(:, 10:end)))];
        meanUtils(k, :) = mean(util, 2);
        
        totalReqs(k, :) =  [cellfun(@(x) str2num(x), D{1, 1}.numRequests)];
        
        [avg_val, avg_idx] = min(avgRT, [], 2);
        [p95_val, p95_idx] = min(p95RT, [], 2);
        [std_val, std_idx] = min(stdRT, [], 2);
    end
    
    
    tmp_struct = struct(  'testName', dataCell{test, 2}, ...
                          'avgRTVal', avgRTVal, ...                
                          'p95RTVal', p95RTVal, ... 
                          'stdRTVal', stdRTVal, ...
                          'meanUtils' , meanUtils, ...
                          'totalReqs', totalReqs);
                      
     testData = [testData; tmp_struct];

end

%% Calculate analytic results and plot results

addpath("opt_clone_funcs")

% Add results for CWR

m = length(LAMBDA_FRAC)
n = length(testData)-1

meanRT_CWR = zeros(m, n/2);
stdRT_CWR = zeros(m, n/2);
meanRT_SED = zeros(m, n/2);
stdRT_SED = zeros(m, n/2);

meanUtil_CWR = zeros(m, n/2);
meanUtil_SED = zeros(m, n/2);

X_CWR = []
X_SED = []

% Read data
for k = 1:m   
    c_CWR = 1;
    c_SED = 1;
    for i = 1:n  
        testName = testData(i+1).testName;
        
        if contains(testName, 'CWR')
            vals = testData(i+1).avgRTVal(k, :);
            meanRT_CWR(k, c_CWR) = mean(vals, 2);
            stdRT_CWR(k, c_CWR) = std(vals, [], 2);
            
            meanUtils_CWR(k, c_CWR) = mean(testData(i+1).meanUtils(k, :));
            c_CWR = c_CWR + 1;
            if k == 1
                X_CWR = [X_CWR, convertCharsToStrings(testData(i+1).testName)];
            end
        elseif contains(testName, 'SED')
            vals = testData(i+1).avgRTVal(k, :);
            meanRT_SED(k, c_SED) = mean(vals, 2);
            stdRT_SED(k, c_SED) = std(vals, [], 2);
            
            meanUtils_SED(k, c_SED) = mean(testData(i+1).meanUtils(k, :));
            c_SED = c_SED + 1;
            if k == 1
                X_SED = [X_SED, convertCharsToStrings(testData(i+1).testName)];
            end
        end

    end
end


%% Save to CSV file

a = open("datafiles/hetero_theory.mat");
meanRT_CWR_theory = a.respTimes;
meanRT_SED_theory = meanRT_CWR_theory;

meanRT_CWR_theory(meanRT_CWR_theory == -1) = inf;
meanRT_SED_theory(meanRT_SED_theory == -1) = inf;

withinSTD =  2.09*stdRT_CWR - abs(meanRT_CWR_theory - meanRT_CWR)

lim_util = 0.05;

[~, minidx_CWR] = min(meanRT_CWR, [], 2);
[~, minidx_SED] = min(meanRT_SED, [], 2);

[~, minidx_CWR_theory] = min(meanRT_CWR_theory, [], 2);

lambda = cellstr(num2str(LAMBDA_FRAC'));
T_CWR = table(lambda);
T_SED = table(lambda);
T_CWR_theory = table(lambda);
T_SED_theory = table(lambda);
% Create table to export
for k = 1:n/2
    
  	CWRcell = cell(m, 1);
    SEDcell = cell(m, 1);
    CWRcell_theory = cell(m, 1);
    SEDcell_theory = cell(m, 1);
    
    for i = 1:m
        if meanUtils_CWR(i, k) < lim_util || (i == 6 && k == 1)
            CWRcell{i} = 'U';
        else
            if minidx_CWR(i) == k
                CWRcell{i} = ['\textbf{' num2str(meanRT_CWR(i, k), '%.2f') '}'];
            else
                CWRcell{i} = num2str(meanRT_CWR(i, k), '%.2f');
            end
        end
        
        if meanUtils_SED(i, k) < lim_util || (i == 6 && k == 1)
            SEDcell{i} = 'U';
        else
            if minidx_SED(i) == k
                SEDcell{i} = ['\textbf{' num2str(meanRT_SED(i, k), '%.2f') '}'];
            else
                SEDcell{i} = num2str(meanRT_SED(i, k), '%.2f');
            end 
        end
        
        if meanRT_CWR_theory(i, k) == inf
            CWRcell_theory{i} = 'U';
        else
            if minidx_CWR_theory(i) == k
                CWRcell_theory{i} = ['\textbf{' num2str(meanRT_CWR_theory(i, k), '%.2f') '}'];
            else
                CWRcell_theory{i} = num2str(meanRT_CWR_theory(i, k), '%.2f');
            end 
        end
            
        
        if meanRT_SED_theory(i, k) == inf
            SEDcell_theory{i} = 'U';
        else
            if k == 3
                SEDcell_theory{i} = num2str(meanRT_CWR_theory(i, k), '%.2f');
            else
                SEDcell_theory{i} = 'S';
            end
        end
        
    end
    
    T_CWR = addvars(T_CWR, CWRcell);
    T_SED = addvars(T_SED, SEDcell);
    T_CWR_theory = addvars(T_CWR_theory, CWRcell_theory);
    T_SED_theory = addvars(T_SED_theory, SEDcell_theory);
end

pnames = {'lambda', 'var1', 'var2', 'var3', 'var4'};
T_CWR.Properties.VariableNames = pnames;
T_SED.Properties.VariableNames = pnames;
T_CWR_theory.Properties.VariableNames = pnames;
T_SED_theory.Properties.VariableNames = pnames;

writetable(T_CWR, "datafiles/table-CWR.csv");
writetable(T_SED, "datafiles/table-SED.csv");
writetable(T_CWR_theory, "datafiles/table-CWR-theory.csv");
writetable(T_SED_theory, "datafiles/table-SED-theory.csv");



%% Compare OptClone in mean and p95 response time

[~, fit_FCFS] = plotting_optClone_meanVsP95(testData_FCFS, CLONES, LAMBDA_FRAC, MC_SIMS, [1, 2, 3, 4]);
[~, fit_PS] = plotting_optClone_meanVsP95(testData_PS, CLONES, LAMBDA_FRAC, MC_SIMS, [1, 2, 3, 4]);




%% Plot amount of requests
    
figure(3)
clf()
sgtitle("Number of request over clone-count")
for i = 1:1
    for k=1:m
        subplot(1, m, k + (i-1)*m)
        reqs = testData(i+1).totalReqs;
        hold on;
        boxplot(reqs', LAMBDA_FRAC)
        title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(k)))
        ylim([0, 1.2*1e6])
        if k == 1
           ylabel(testData(i+1).testName)
        end
    end
end


%% Save to CSV


    
csvwrite(['csvfiles/minAvgRTSer_mean' s '.csv'], [U, mean(minAvgRTSer, 2)]);
csvwrite(['csvfiles/minAvgRTSer_min' s '.csv'], [U, min(minAvgRTSer, [], 2)]);
csvwrite(['csvfiles/minAvgRTSer_max' s '.csv'], [U, max(minAvgRTSer, [], 2)]);
csvwrite(['csvfiles/minAvgRTVal_mean' s '.csv'], [U, mean(minAvgRTVal, 2)]);

csvwrite('csvfiles/minAvgRTSer_minmax.csv', [ [U; flipud(U)], ...
    [max(minAvgRTSer, [], 2); flipud(min(minAvgRTSer, [], 2))]]);

csvwrite(['csvfiles/utils-1-sim' s '.csv'], [x1, y1]);
csvwrite(['csvfiles/utils-4-sim' s '.csv'], [x2, y2]);
csvwrite(['csvfiles/utils-8-sim' s '.csv'], [x3, y3]);



%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "c")), split);
end
