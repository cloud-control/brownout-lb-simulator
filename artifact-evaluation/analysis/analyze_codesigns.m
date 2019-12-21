%% Get the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!
clc
clear all;

addpath('./functions')

if ~isfile('codesigns.mat')
    path = '../simulation-results/co-designs';
    
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 2);
    
    for k = 1:m
        k
        dataCell{k, 1} = read_mcData([path '/' tests(k).name]);
        dataCell{k, 2} = tests(k).name;
    end
    
    save('codesigns.mat', 'dataCell');
else
    tmp = load('codesigns.mat');
    dataCell = tmp.dataCell;
    m = length(dataCell);
end

%% Process the data

LAMBDA_FRAC = [0.3, 0.38, 0.52, 0.62, 0.7];
CLONES = [1, 2, 3, 4, 6, 12]; 
MC_SIMS = 20

m = size(dataCell, 1);

testData_PS = struct(  'testName', [], ...
                    'minAvgRTVal', [], ...
                    'minAvgRTSer', []);
                    
for test = 1:m
       
    data = dataCell{test, 1};
    
    % Find the best cloning for each arrival rate frac
    split = cellfun(@(x) strsplit(x, 'af'), data(:, 2), 'UniformOutput', false);
    vals = cellfun(@(x) x{2}, split, 'UniformOutput', false);
    rates = sort(unique(cellfun(@(x) str2num(x), vals)));

    lenRate = length(rates);

    minAvgRTVal = zeros(lenRate, MC_SIMS);
    minAvgRTSer = zeros(lenRate, MC_SIMS);
    
    for k = 1:lenRate
        rate = rates(k);
        ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
        disp([num2str(rate) ' ' num2str(size(data(ind, :), 1))])

        D = data(ind, :);
        [m, ~] = size(D);
        avgRT = zeros(MC_SIMS, m);
        for i = 1:m
            avgRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.avgResponseTime);
        end

        [avg_val, avg_idx] = min(avgRT, [], 2);

        minAvgRTVal(k, :) = avg_val;
        minAvgRTSer(k, :) = getServerIdx(D, avg_idx);
    end
    
    
    tmp_struct = struct(  'testName', dataCell{test, 2}, ...
        'minAvgRTVal', minAvgRTVal, ...
        'minAvgRTSer', minAvgRTSer);

    testData_PS = [testData_PS; tmp_struct];


end

%% Write to csv

for k = 2:3
    respResults = zeros(length(LAMBDA_FRAC)*2, 1);
    cloneResults = zeros(length(LAMBDA_FRAC)*2, 1);
    rates = zeros(length(LAMBDA_FRAC)*2, 1);
    for i = 1:length(LAMBDA_FRAC)
        respmean = mean(testData_PS(k).minAvgRTVal(i,:));
        clonemean = mean(testData_PS(k).minAvgRTSer(i,:));
        
        respResults(2*i-1) = respmean;
        respResults(2*i) = respmean;     
        cloneResults(2*i-1) = clonemean;
        cloneResults(2*i) = clonemean;
        rates(2*i-1) = LAMBDA_FRAC(i)-0.02;
        rates(2*i) = LAMBDA_FRAC(i)+0.02;
    end
    
    csvwrite(['../plots/data/co-design/' testData_PS(k).testName '-RT.csv'], [rates, respResults]);
    csvwrite(['../plots/data/co-design/' testData_PS(k).testName '-clone.csv'], [rates, cloneResults]);
    
end
    
    
%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "c")), split);
end