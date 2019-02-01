
%% Old reading
% Each run subfolder must contain the same amount of folders

basepath = '/home/johanr/Projects/brownout-lb-simulator/result_RIQvsIQ';

subfolders = dir(basepath);
subfolders(1:2) = [];

strats = dir([basepath '/' subfolders(1).name]);
strats(1:2) = [];

m = length(subfolders);
n = length(strats);
paths = cell(m, n);

for i = 1:m
    for j = 1:n
        paths{i, j} = [basepath  '/run' num2str(i-1)  '/'  ...
            strats(j).name '/sim-final-results.csv'];
   end
end

data = read_paths(paths, strats);

%% New reading
% Each run subfolder must contain the same amount of folders

basepath = '/home/johanr/Projects/brownout-lb-simulator/result_RIQvsIQ6';

strats = dir(basepath);
strats(1:2) = [];

m = length(strats)

paths = cell(m, 1)
for i = 1:m
    runs =  dir([basepath '/' subfolders(i).name]);
    runs(1:2) = [];
    n = length(runs)
    
    subpaths = cell(n,1)
    for j = 1:n
        subpaths{j} = [basepath '/' strats(i).name  '/run' num2str(j-1) ...
            '/sim-final-results.csv'];
    end
    
    paths{i} = subpaths
end

data = read_paths(paths, strats);

%% Plot data

XMIN = 0.1
XMAX = 0.9
YMIN = 0
YMAX = 20

COMPARE = [2, 5]


% Plot all
figure(1)
clf()
for k = 1:m
    x = data{k, 1}.arrivalRateFrac;
    T = data{k, 1}.avgResponseTime;
    T95 = data{k, 1}.p95ResponseTime;
    U = calc_utilization(data{k, 1});
    
    subplot(2, m, k)
    hold on;
    plot(x, T, 'b','LineWidth', 2);
    plot(x, T95, 'b:');
    legend("avgRT", "\sigma_{95}RT", 'Location', 'NorthWest')
    title(data{k, 2})
    ylabel("Response time")
    xlabel("Arrival rate fraction")
    xlim([XMIN XMAX])
    ylim([YMIN YMAX])

    subplot(2, m, m+k)
    hold on;
    plot(x, mean(U, 2))
    xlim([XMIN XMAX])
    ylabel("Utilization")
    xlabel("Arrival rate fraction")

end

% Plot against
figure(2)
clf()
for k = 1:length(COMPARE)
    ind = COMPARE(k)
    x = data{ind, 1}.arrivalRateFrac;
    T = data{ind, 1}.avgResponseTime;
    T95 = data{ind, 1}.p95ResponseTime;
    U = calc_utilization(data{ind, 1});
    
    subplot(3, 1, 1)
    hold on;
    plot(x, T,'LineWidth', 2);
    
    subplot(3, 1, 2)
    hold on;
    plot(x, T95);
    
    subplot(3, 1, 3)
    hold on;
    plot(x, mean(U, 2))
end
subplot(3, 1, 1)
title("Compare")
ylabel("Resp. time")
xlabel("Arrival rate fraction")
xlim([XMIN XMAX])
ylim([YMIN YMAX])
legend(data(COMPARE,2), 'Location', 'NorthWest')
subplot(3, 1, 2)
ylabel("\sigma_{95} resp. time")
xlabel("Arrival rate fraction")
xlim([XMIN XMAX])
ylim([YMIN YMAX])
legend(data(COMPARE,2), 'Location', 'NorthWest')
subplot(3, 1, 3)
xlim([XMIN XMAX])
ylabel("Utilization")
xlabel("Arrival rate fraction")
legend(data(COMPARE,2), 'Location', 'NorthWest')

A = calc_utilization(data{1,1});

function U = calc_utilization(table)
    m = size(table, 1);
    servers = sum(cellfun(@(x) contains(x, 'Util'), ...
        table.Properties.VariableNames));
    U = zeros(m, servers);
    for i = 1:servers
        U(:, i) = eval(['table.s' num2str(i-1) 'Util']);
    end
end
    
    


