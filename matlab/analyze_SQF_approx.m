
% Generate mean response time from SQF approximations

util = linspace(0.1, 0.9, 20);
nbrServers = [4, 6, 8, 10, 12, 14];
mu = 1;
lambda = util'*nbrServers;

% Calculate coefficient of variation
Ca = sqrt(lambda) ./ (lambda); %Assuming poisson

% Cs hyperexponential
p1 = 0.95; p2 = 0.05;
mu1 = 8.95; mu2 = 0.45;
mu_hypo = p1/mu1 + p2/mu2;
sig_hypo = sqrt(2*(p1/mu1^2 + p2/mu2^2) - (p1/mu1 + p2/mu2)^2);
Cs_sxmodel = sqrt(14.7736) %sqrt(10); %sig_hypo/mu_hypo;

% For testing
%p1 = 0.; p2 = 0.05;
%mu1 = 8.95; mu2 = 0.45;
%mu_hypo = 
%sig_hypo = 

[m, n] = size(lambda);
RT_sqf_ps_approx = zeros(m, n);
RT_sqf_fcfs_approx_sxmodel = zeros(m, n);
RT_sqf_fcfs_approx_expon = zeros(m, n);

for i = 1:n
    for k = 1:m
        RT_sqf_ps_approx(k, i) = SQFapprox_ps(lambda(k, i), mu, nbrServers(i));
        RT_sqf_fcfs_approx_sxmodel(k, i) = SQFapprox_fcfs(lambda(k, i), mu, nbrServers(i), Ca(k, i), Cs_sxmodel);
        RT_sqf_fcfs_approx_expon(k, i) = SQFapprox_fcfs(lambda(k, i), mu, nbrServers(i), Ca(k, i), 1);
    end
end

% Read the data from simulations
basepath = '/home/johan/Projects/brownout-lb-simulator/result_SQFapprox';
data = read_data(basepath);


%% Analyze SQF-FCFS approx according to Nelsson1993

util = linspace(0.1, 0.9, 20);
nbrServers = [4, 6, 8, 10, 12, 14];
mu = 1;
lambda = util'*nbrServers;

% Calculate coefficient of variation
Ca = sqrt(lambda) ./ (lambda); %Assuming poisson

% Cs hyperexponential
p1 = 0.95; p2 = 0.05;
mu1 = 8.95; mu2 = 0.45;
mu_hypo = p1/mu1 + p2/mu2;
sig_hypo = sqrt(2*(p1/mu1^2 + p2/mu2^2) - (p1/mu1 + p2/mu2)^2);
Cs_sxmodel = sqrt(14.7736) %sqrt(10); %sig_hypo/mu_hypo;

[m, n] = size(lambda);
RT_sqf_fcfs_approx_sxmodel = zeros(m, n);
RT_sqf_fcfs_approx_expon = zeros(m, n);

for i = 1:n
    for k = 1:m
        RT_sqf_fcfs_approx_sxmodel(k, i) = SQFapprox_fcfs(lambda(k, i), mu, nbrServers(i), Ca(k, i), Cs_sxmodel);
        RT_sqf_fcfs_approx_expon(k, i) = SQFapprox_fcfs(lambda(k, i), mu, nbrServers(i), Ca(k, i), 1);
    end
end

% Read the data from simulations
basepath = '/home/johan/Projects/brownout-lb-simulator/result_SQFapprox';
data = read_data(basepath);


% SXmodel
order = [10, 11, 12, 7, 8, 9]; % Change this if necessary
figure(1)
clf()
for i = 1:n
    subplot(2, 3, i)
    hold on;
    plot(util, data{order(i), 1}.avgResponseTime, "b", 'linewidth', 2)
    plot(util, RT_sqf_fcfs_approx_sxmodel(:, i), "k--", 'linewidth', 2)
    xlabel("utilization")
    ylabel("mean resp. time")
    xlim([0, 1])
    ylim([0, 1.2*max(max(data{order(i), 1}.avgResponseTime, ...
        RT_sqf_fcfs_approx_sxmodel(:, i)))])
    %title(['Using ' data{order(i), 2}])
    legend(data{order(i), 2}, ['approx SQF-' num2str(nbrServers(i))], ...
        'location', 'northwest')
end
subplot(2, 3, 2)
title("SQF-FCFS; using SXmodel as service rate")

% Expon
order = [4, 5, 6, 1, 2, 3]; % Change this if necessary
figure(2)
clf()
for i = 1:n
    subplot(2, 3, i)
    hold on;
    plot(util, data{order(i), 1}.avgResponseTime, "b", 'linewidth', 2)
    plot(util, RT_sqf_fcfs_approx_expon(:, i), "k--", 'linewidth', 2)
    xlim([0, 1])
    ylim([0, 1.2*max(max(data{order(i), 1}.avgResponseTime, ...
        RT_sqf_fcfs_approx_expon(:, i)))])
    xlabel("utilization")
    ylabel("mean resp. time")
    %title(['Using ' data{order(i), 2}])
    legend(data{order(i), 2}, ['approx SQF-' num2str(nbrServers(i))], ...
        'location', 'northwest')
end
subplot(2, 3, 2)
title("SQF-FCFS; using exponential service rate")

%% Analyze SQF-PS approx according to Gupta2007
util = linspace(0.1, 0.9, 20);
nbrServers = [4, 6, 8, 10, 12, 14];
mu = 1;
lambda = util'*nbrServers;

% Calculate coefficient of variation
Ca = sqrt(lambda) ./ (lambda); %Assuming poisson

% Cs hyperexponential
p1 = 0.95; p2 = 0.05;
mu1 = 8.95; mu2 = 0.45;
mu_hypo = p1/mu1 + p2/mu2;
sig_hypo = sqrt(2*(p1/mu1^2 + p2/mu2^2) - (p1/mu1 + p2/mu2)^2);
Cs_sxmodel = sqrt(14.7736) %sqrt(10); %sig_hypo/mu_hypo;

[m, n] = size(lambda);
RT_sqf_ps_approx_sxmodel = zeros(m, n);
RT_sqf_ps_approx_expon = zeros(m, n);

for i = 1:n
    for k = 1:m
        RT_sqf_ps_approx_sxmodel(k, i) = SQFapprox_ps(lambda(k, i), mu, nbrServers(i));
        RT_sqf_ps_approx_expon(k, i) = SQFapprox_ps(lambda(k, i), mu, nbrServers(i));
    end
end
% Read the data from simulations
basepath = '/home/johan/Projects/brownout-lb-simulator/result_SQFapprox';
data = read_data(basepath);


% SXmodel
order = [22, 23, 24, 19, 20, 21]; % Change this if necessary
figure(1)
clf()
for i = 1:n
    subplot(2, 3, i)
    hold on;
    plot(util, data{order(i), 1}.avgResponseTime, "b", 'linewidth', 2)
    plot(util, RT_sqf_ps_approx_sxmodel(:, i), "k--", 'linewidth', 2)
    xlabel("utilization")
    ylabel("mean resp. time")
    xlim([0, 1])
    ylim([0, 1.2*max(max(data{order(i), 1}.avgResponseTime, ...
        RT_sqf_ps_approx_sxmodel(:, i)))])
    %title(['Using ' data{order(i), 2}])
    legend(data{order(i), 2}, ['approx SQF-' num2str(nbrServers(i))], ...
        'location', 'northwest')
end
subplot(2, 3, 2)
title("SQF-PS; using SXmodel as service rate")

% Expon
order = [16, 17, 18, 13, 14, 15];% Change this if necessary
figure(2)
clf()
for i = 1:n
    subplot(2, 3, i)
    hold on;
    plot(util, data{order(i), 1}.avgResponseTime, "b", 'linewidth', 2)
    plot(util, RT_sqf_ps_approx_expon(:, i), "k--", 'linewidth', 2)
    xlim([0, 1])
    ylim([0, 1.2*max(max(data{order(i), 1}.avgResponseTime, ...
        RT_sqf_ps_approx_expon(:, i)))])
    xlabel("utilization")
    ylabel("mean resp. time")
    %title(['Using ' data{order(i), 2}])
    legend(data{order(i), 2}, ['approx SQF-' num2str(nbrServers(i))], ...
        'location', 'northwest')
end
subplot(2, 3, 2)
title("SQF-PS; using exponential service rate")

%%
% Plot the data
%{
figure(1)
clf()
hold on;
plot(util, data{4, 1}.avgResponseTime, "b", 'linewidth', 2)
plot(util, data{3, 1}.avgResponseTime, "r", 'linewidth', 2)
plot(util, RT_sqf_ps_approx, "k--", 'linewidth', 2)
legend("SQF ps SXmodel", "SQF ps expon", "SQF ps approx", 'location', 'northwest')
ylim([0, 1.2*max(RT_sqf_ps_approx)])
xlim([0, 1])


figure(2)
clf()
subplot(2, 1, 1)
hold on;
plot(util, data{2, 1}.avgResponseTime, "b", 'linewidth', 2)
plot(util, RT_sqf_fcfs_approx(:, 1), "k--", 'linewidth', 2)
xlim([0, 1])
subplot(2, 1, 2)
hold on;
plot(util, data{1, 1}.avgResponseTime, "b", 'linewidth', 2)
plot(util, RT_sqf_fcfs_approx(:, 2), "k--", 'linewidth', 2)
xlim([0, 1])
%}



