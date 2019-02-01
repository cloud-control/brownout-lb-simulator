path = '/home/johanr/Projects/brownout-lb-simulator/result_minComp';

RT = dir(path);
RT(1:2) = [];
m = size(RT, 1);

data = cell(m, 1);

for k = 1:m
    table = readtable([ path '/' RT(k).name], 'Delimiter', ',');
    data{k} = table.Var1;
end

vec = linspace(0,8,10000);
cdfs = cell(m, 1)
for k = 1:m
    [cdfs{k}, ~] = histcounts(data{k}, vec, 'Normalization', 'cdf');
end

figure(1)
clf()
hold on;
plot(vec(1:end-1), cdfs{1}, 'g', 'LineWidth', 1);
plot(vec(1:end-1), cdfs{2}, 'r--', 'LineWidth', 1);