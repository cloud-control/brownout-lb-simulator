clear; clc;
preprocessData;
load('data.mat');

%%
[~,order] = sort([data(:).performance],'descend');
names={data(:).name};
Tau = zeros(length(data(1).max_latencies(:,1)),length(data));
means = zeros(length(data),1);
% trmeans = zeros(length(data),1);
for i=1:length(data)
    Tau(:,i)  = max(data(i).max_latencies,[],2);
    means(i)  = nanmean(Tau(:,i));
%     trmeans(i)= trimmean(Tau(:,i),99);
end
boxplot(Tau(:,order),{names{order}});
hold on;
plot(means(order),'k.');
% plot(trmeans,'rx');
