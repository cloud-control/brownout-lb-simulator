%% Read the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

READ_NEW = 1;

if READ_NEW
    path = '/home/johanr/Projects/brownout-lb-simulator/result_opt_clone-ps';
    data = read_mcData(path);
    save('datafiles/data-opt_clone.mat', 'data');
else
    tmp = load('datafiles/data-opt_clone.mat');
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
    
    % bugcheck
    %if size(data(ind, :), 1) ~= NBR_OF_DIFF_SERVERS
    %    error("Wrong number of servers found!")
    %end
    
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


%% Plot optimal servers

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
ylim([0, 10])
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


%% Plot Utilization

U = rates*0.01 + 0.05;
sIdx = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3];
show = [1, 4, 8]

Y = zeros(length(meanUtils), length(show));

for i = 1:length(show)
    for k = 1:length(meanUtils)
        u = meanUtils{k};
        if length(u) >= show(i)
            if length(u) == 12
                Y(k, i) = u(sIdx(show(i)));
            elseif length(u) == 11
                Y(k, i) = u(sIdx(show(i))-1);
            elseif length(u) == 10
                Y(k, i) = u(sIdx(show(i))-2);
            else
                Y(k, i) = u(show(i));
            end
            
        end
    end
end

figure(4)
clf()
hold on;
plot(U, Y(:, 1), "k", 'LineWidth', 2)
plot(U, Y(:, 2), "b", 'LineWidth', 2)
plot(U, Y(:, 3), "r", 'LineWidth', 2)
xlim([0, 1])
ylim([0, 1])


%% Save to CSV


csvwrite('csvfiles/minAvgRTSer_mean.csv', [U, mean(minAvgRTSer, 2)]);
csvwrite('csvfiles/minAvgRTSer_min.csv', [U, min(minAvgRTSer, [], 2)]);
csvwrite('csvfiles/minAvgRTSer_max.csv', [U, max(minAvgRTSer, [], 2)]);
csvwrite('csvfiles/minAvgRTVal_mean.csv', [U, mean(minAvgRTVal, 2)]);

csvwrite('csvfiles/minAvgRTSer_minmax.csv', [ [U; flipud(U)], ...
    [max(minAvgRTSer, [], 2); flipud(min(minAvgRTSer, [], 2))]]);

csvwrite('csvfiles/utils-1-sim.csv', [x1, y1]);
csvwrite('csvfiles/utils-4-sim.csv', [x2, y2]);
csvwrite('csvfiles/utils-8-sim.csv', [x3, y3]);

%% Functions

function sIdx = getServerIdx(data, idx)
    split = cellfun(@(x) strsplit(x, '_'), data(idx, 2), ...
        'UniformOutput', false);
    sIdx = cellfun(@(x) str2num(erase(x{1}, "s")), split);
end
