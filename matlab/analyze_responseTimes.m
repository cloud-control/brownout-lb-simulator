
%% For the G/G/1-equivalent example.
path = '/home/johanr/Projects/brownout-lb-simulator/result_gg1Example';

data = read_respTimes(path);

[m, n] = size(data)

vec = linspace(0,10,1000);
cdfs = cell(m, n-1);
for i = 1:m
    for k = 1:n-1
        [cdfs{i, k}, ~] = histcounts(data{i, k+1}, vec, 'Normalization', 'cdf');
    end
end


%% Plot all
figure(1)
clf()
subplot(1,2,1)
hold on;
for k = 1:n-1
    plot(vec(1:end-1), cdfs{1, k}, 'g', 'LineWidth', 1);
    plot(vec(1:end-1), cdfs{3, k}, 'r--', 'LineWidth', 1);
end
axis([0 10 0 1])
legend(data{1, 1}, data{3, 1})

subplot(1,2,2)
hold on;
for k = 1:n-1
    plot(vec(1:end-1), cdfs{2, k}, 'g', 'LineWidth', 1);
    plot(vec(1:end-1), cdfs{4, k}, 'r--', 'LineWidth', 1);
end
axis([0 10 0 1])
legend(data{2, 1}, data{4, 1})


%% Save to CSV format

for k = 1:4
    csvwrite([data{k,1}, '.csv'], [vec(1:end-1)' cdfs{k, 1}']);
end
