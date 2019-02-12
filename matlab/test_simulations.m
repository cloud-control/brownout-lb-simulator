
basepath = '/home/johanr/Projects/brownout-lb-simulator';

n = 10;
paths = cell(n, 1);
for k = 0:n-1
    paths{k+1, 1} = [basepath '/result/run' num2str(k, '%d') '/RIQ-d/sim-final-results.csv'];
end

data = read_paths(paths);

%% Plot data

y = data.avgResponseTime;
x = 1:length(y);
[l, u] = calc_rT_bounds(data);

figure(1)
clf()
hold on;
plot(x, y, 'b', 'LineWidth', 2)
plot(x, l, 'k--', 'LineWidth', 1)
plot(x, u, 'k--', 'LineWidth', 1)
legend("RIQ-q", 'Location', 'NorthWest')
title("Expected value for response time T")
ylabel("Response time")
xlabel("Simulation")

U_RIQ = zeros(100, 12);
U_CR = zeros(100, 12);
for k = 0:11
    U_RIQ(:, k+1) = eval(['data_RIQ.ServerUtilization' num2str(k)]);
    U_CR(:, k+1) = eval(['data_CR.ServerUtilization' num2str(k)]);
end

figure(2)
clf()
hold on;
for k = 0:11
    plot(x_RIQ, mean(U_RIQ, 2), 'b', 'LineWidth', 2)
    plot(x_CR, mean(U_CR, 2), 'r', 'LineWidth', 2)
end
legend("RIQ-q", "Clone Random to 4", 'Location', 'NorthWest')
title("Mean utilization")
ylabel("Utilization")
xlabel("Arrival rate fraction")

function [lower, upper] =  calc_rT_bounds(data)
    y = data.avgResponseTime
    s = data.stddevResponseTime
    N = data.numRequests
    
    upper = zeros(size(y))
    lower = zeros(size(y))
    for k = 1:length(y)
       lower(k) = y(k) - 1.96*s(k) / sqrt(N(k));
       upper(k) = y(k) + 1.96*s(k) / sqrt(N(k));
    end
end

