
% Generate mean response time from SQF approximations

util = linspace(0.1, 0.9, 10);
nbrServers = 12;
mu = 1;
lambda = util*nbrServers;

% Calculate coefficient of variation
Ca = sqrt(lambda) ./ (lambda); %Assuming poisson

% Cs hyperexponential
%p1 = 0.95; p2 = 0.05;
%mu1 = 8.95; mu2 = 0.45;
%mu_hypo = p1/mu1 + p2/mu2;
%sig_hypo = sqrt(2*(p1/mu1^2 + p2/mu2^2) - (p1/mu1 + p2/mu2)^2);
%Cs_sxmodel = sqrt(14.7736) %sqrt(10); %sig_hypo/mu_hypo;

% For testing
p1 = 0.; p2 = 0.05;
mu1 = 8.95; mu2 = 0.45;
mu_hypo = 
sig_hypo = 


m = length(lambda);
RT_sqf_ps_approx = zeros(m, 1);
RT_sqf_fcfs_approx = zeros(m, 1);

for k = 1:m
    RT_sqf_ps_approx(k) = SQFapprox_ps(lambda(k), mu, nbrServers);
    RT_sqf_fcfs_approx(k) = SQFapprox_fcfs(lambda(k), mu, nbrServers, Ca(k), Cs_sxmodel);
end

% Read the data from simulations
basepath = '/home/johanr/Projects/brownout-lb-simulator/result_SQF';
data = read_data(basepath);


%%
% Plot the data
figure(1)
clf()
hold on;
plot(util, data{3, 1}.avgResponseTime, "b", 'linewidth', 2)
plot(util, data{4, 1}.avgResponseTime, "r", 'linewidth', 2)
plot(util, RT_sqf_ps_approx, "k--", 'linewidth', 2)
legend("SQF ps SXmodel", "SQF ps expon", "SQF ps approx", 'location', 'northwest')
ylim([0, 1.2*max(RT_sqf_ps_approx)])
xlim([0, 1])

figure(2)
clf()
hold on;
plot(util, data{1, 1}.avgResponseTime, "b", 'linewidth', 2)
plot(util, RT_sqf_fcfs_approx, "k--", 'linewidth', 2)
xlim([0, 1])


