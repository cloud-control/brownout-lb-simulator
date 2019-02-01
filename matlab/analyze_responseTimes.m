path = '/local/home/tommi/CloudControl/cloning/brownout-lb-simulator/mintest';

RT = dir(path);
RT(1:2) = [];
m = size(RT, 1);

data = cell(m, 2);

for k = 1:m
    table = readtable([ path '/' RT(k).name], 'Delimiter', ',');
    data{k, 1} = table.Var1;
    data{k, 2} = RT(k).name;
end

vec = linspace(0,10,10000);
cdfs = cell(m, 1);
for k = 1:m
    [cdfs{k}, ~] = histcounts(data{k}, vec, 'Normalization', 'cdf');
end

%%
CHOOSE = [2 4];

figure(1)
clf()
subplot(1,2,1)
hold on;
plot(vec(1:end-1), cdfs{CHOOSE(1)}, 'g', 'LineWidth', 1);
plot(vec(1:end-1), cdfs{CHOOSE(2)}, 'r--', 'LineWidth', 1);
axis([0 10 0 1])
legend(data(CHOOSE, 2))

CHOOSE = [1 3];
subplot(1,2,2)
hold on;
plot(vec(1:end-1), cdfs{CHOOSE(1)}, 'g', 'LineWidth', 1);
plot(vec(1:end-1), cdfs{CHOOSE(2)}, 'r--', 'LineWidth', 1);
axis([0 10 0 1])
legend(data(CHOOSE, 2))