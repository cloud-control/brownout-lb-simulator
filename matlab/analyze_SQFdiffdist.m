%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

READ_NEW = 1;

if READ_NEW
    path = '/home/johanr/Projects/brownout-lb-simulator/result_SQFdiffDist';
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 2);
    
    for k = 1:m
        k
        dataCell{k, 1} = read_mcData([path '/' tests(k).name]);
        dataCell{k, 2} = tests(k).name;
    end
    
    save('datafiles/data-SQFdiffDist.mat', 'dataCell');
else
    tmp = load('datafiles/data-SQFdiffDist.mat');
    dataCell = tmp.dataCell;
end

%% Process data

MC_SIMS = 20;

testData = struct(  'testName', [], ...
                    'avgRTVal', [], ...                
                    'p95RTVal', [], ... 
                    'stdRTVal', [], ...
                    'meanUtils' , [], ...
                    'totalReqs', []);
for test = 1:m
       
    data = dataCell{test, 1};
    
    % Extract sortedmetrics for each cloning value
    
    split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
    vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
    rates = sort(unique(cellfun(@(x) str2num(x), vals)));
    
    
    cvals = cellfun(@(x) x{1},  split, 'UniformOutput', false);
    clones = sort(unique(cellfun(@(x) str2num(strip(strip(x, "_"), "c")), ...
        cvals)));
    
    lenRate = length(rates);
    lenClone = length(clones)
    
    avgRTVal = zeros(lenRate, MC_SIMS, lenClone);
    p95RTVal = zeros(lenRate, MC_SIMS, lenClone);
    stdRTVal = zeros(lenRate, MC_SIMS, lenClone);
    meanUtils = zeros(lenRate, MC_SIMS, lenClone);
    totalReqs = zeros(lenRate, MC_SIMS, lenClone);
    
    
    for i = 1:lenClone
        for j = 1:lenRate
            clone = clones(i);
            rate = rates(j);
            
            ind_rate = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
            disp(['Rate/nbr of indices : ' num2str(rate) '/' num2str(size(data(ind_rate, :), 1))])
            D = data(ind_rate, :);
            
            ind_clone = cellfun(@(x) startsWith(x, ['c' num2str(clone)]), D(:, 2));
            disp(['Clone/nbr of indices : ' num2str(clone) '/' num2str(size(D(ind_clone, :), 1))])
            D = D(ind_clone, :);
            
            if sum(ind_clone) > 1
                error("More than one clone/arrival fraction found!")
            end
            
            if sum(ind_clone) == 1
                avgRTVal(j, :, i) = cellfun(@(x) str2num(x), D{1, 1}.avgResponseTime);
                p95RTVal(j, :, i) = cellfun(@(x) str2num(x), D{1, 1}.p95ResponseTime);
                stdRTVal(j, :, i) = cellfun(@(x) str2num(x), D{1, 1}.stddevResponseTime);

                util = [cellfun(@(x) str2num(x), table2cell(D{1,1}(:, 10:end)))];
                meanUtils(j, :, i) = mean(util, 2);

                totalReqs(j, :, i) =  [cellfun(@(x) str2num(x), D{1, 1}.numRequests)];
            end
            
        end
    end
    
    tmp_struct = struct(  'testName', dataCell{test, 2}, ...
                          'avgRTVal', avgRTVal, ...                
                          'p95RTVal', p95RTVal, ... 
                          'stdRTVal', stdRTVal, ...
                          'meanUtils' , meanUtils, ...
                          'totalReqs', totalReqs);
                      
     testData = [testData; tmp_struct];

end

%% Plot data

af_dolly = 0.1:0.05:0.7;
af_shiftExp = 0.1:0.05:0.7;
af_hyperExp = 0.2:0.05:1.4;

% 2 - non sync, 5 - sync
rt_c2_ns_dolly = mean(testData(2).avgRTVal(:,:, 1), 2)
rt_c2_s_dolly = mean(testData(5).avgRTVal(:,:, 1), 2)
rt_c4_ns_dolly = mean(testData(2).avgRTVal(:,:, 3), 2)
rt_c4_s_dolly = mean(testData(5).avgRTVal(:,:, 3), 2)
figure(1)
clf()
title("Dolly")
hold on;
plot(af_dolly, rt_c2_ns_dolly, "b--")
plot(af_dolly, rt_c2_s_dolly, "b")
plot(af_dolly, rt_c4_ns_dolly, "r--")
plot(af_dolly, rt_c4_s_dolly, "r")
legend("c2 no sync", "c2 sync", "c4 no sync", "c4 sync", "location", "northwest")
ylim([0, 1])

% 3 - non sync, 6 - sync
rt_c2_ns_hyperExp = mean(testData(3).avgRTVal(:,:, 1), 2)
rt_c2_s_hyperExp = mean(testData(6).avgRTVal(:,:, 1), 2)
rt_c4_ns_hyperExp = mean(testData(3).avgRTVal(:,:, 2), 2)
rt_c4_s_hyperExp = mean(testData(6).avgRTVal(:,:, 2), 2)
figure(3)
clf()
title("HyperExp")
hold on;
plot(af_hyperExp, rt_c2_ns_hyperExp, "b--")
plot(af_hyperExp, rt_c2_s_hyperExp, "b")
plot(af_hyperExp, rt_c4_ns_hyperExp, "r--")
plot(af_hyperExp, rt_c4_s_hyperExp, "r")
legend("c2 no sync", "c2 sync", "c4 no sync", "c4 sync", "location", "northwest")
ylim([0, 0.6])

%% Save to CSV file

csvwrite('csvfiles/rt_c2_ns_dolly.csv', [af_dolly', rt_c2_ns_dolly]);
csvwrite('csvfiles/rt_c2_s_dolly.csv', [af_dolly', rt_c2_s_dolly]);
csvwrite('csvfiles/rt_c4_ns_dolly.csv', [af_dolly(1:end-1)', ...
                                        rt_c4_ns_dolly(1:end-1)]);
csvwrite('csvfiles/rt_c4_s_dolly.csv', [af_dolly(1:end-1)', ...
                                        rt_c4_s_dolly(1:end-1)]);

csvwrite('csvfiles/rt_c2_ns_hyperExp.csv', [af_hyperExp', rt_c2_ns_hyperExp]);
csvwrite('csvfiles/rt_c2_s_hyperExp.csv', [af_hyperExp', rt_c2_s_hyperExp]);
csvwrite('csvfiles/rt_c4_ns_hyperExp.csv', [af_hyperExp', rt_c4_ns_hyperExp]);
csvwrite('csvfiles/rt_c4_s_hyperExp.csv', [af_hyperExp', rt_c4_s_hyperExp]);


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
