%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

READ_NEW = 0;

if READ_NEW
    path = '/home/johanr/Projects/brownout-lb-simulator/result_opt_clone';
    data = read_mcData(path);
    save('data-opt_clone.mat', 'data');
else
    tmp = load('data-opt_clone.mat');
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

for k = 1:lenRate
    rate = rates(k);
    ind = cellfun(@(x) endsWith(x, ['af' num2str(rate)]), data(:, 2));
    
    
    disp([num2str(rate) ' ' num2str(size(data(ind, :), 1))])
    
    % bugcheck
    %if size(data(ind, :), 1) ~= NBR_OF_DIFF_SERVERS
    %    error("Wrong number of servers found!")
    %end
    
    D = data(ind, :);
    [m, ~] = size(D);
    avgRT = zeros(MC_SIMS, m);
    p95RT = zeros(MC_SIMS, m);
    stdRT = zeros(MC_SIMS, m);
    for i = 1:m
        avgRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.avgResponseTime);
        p95RT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.p95ResponseTime);
        stdRT(:, i) = cellfun(@(x) str2num(x), D{i, 1}.stddevResponseTime);
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
end



%% Plot results

U = rates*0.01 + 0.05
conf = std(minAvgRTVal, [], 2) * 2.09 / sqrt(20)

figure(1)
clf()
hold on;
yyaxis left
plot(U, mean(minAvgRTSer, 2), 'r', 'LineWidth', 2)
plot(U, max(minAvgRTSer, [], 2), 'k--')
plot(U, min(minAvgRTSer, [], 2), 'k--')
ylim([0, 10])
yyaxis right
plot(U, mean(minAvgRTVal, 2), 'b', 'LineWidth', 2)
plot(U, mean(minAvgRTVal, 2) + conf, 'k--', 'LineWidth', 2)
plot(U, mean(minAvgRTVal, 2) - conf, 'k--', 'LineWidth', 2)
title("For avg. Response Time")
xlim([0, 0.7])
ylim([0, 20])
grid on;

figure(2)
clf()
hold on;
yyaxis left
plot(U, mean(minP95RTSer, 2), 'r', 'LineWidth', 2)
plot(U, max(minP95RTSer, [], 2), 'k--')
plot(U, min(minP95RTSer, [], 2), 'k--')
ylim([0, 10])
yyaxis right
plot(U, mean(minP95RTVal, 2), 'b', 'LineWidth', 2)
title("For p95 Response Time")
xlim([0, 0.7])
%ylim([0, 20])
grid on;

figure(3)
clf()
hold on;
yyaxis left
plot(U, mean(minStdRTSer, 2), 'r', 'LineWidth', 2)
plot(U, max(minStdRTSer, [], 2), 'k--')
plot(U, min(minStdRTSer, [], 2), 'k--')
ylim([0, 10])
yyaxis right
plot(U, mean(minStdRTVal, 2), 'b', 'LineWidth', 2)
title("For stddev Response Time")
xlim([0, 0.7])
%ylim([0, 20])
grid on;

%% Save to CSV

csvwrite('minAvgRTSer_mean.csv', [U, mean(minAvgRTSer, 2)]);
csvwrite('minAvgRTSer_min.csv', [U, min(minAvgRTSer, [], 2)]);
csvwrite('minAvgRTSer_max.csv', [U, max(minAvgRTSer, [], 2)]);
csvwrite('minAvgRTSer_RT.csv', [U, mean(minAvgRTVal, 2)]);

%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "s")), split);
end
