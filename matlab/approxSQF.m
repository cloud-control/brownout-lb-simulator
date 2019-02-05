% Get mean RT for SQF using PS as queuing disciplin
util = 0.7;
nbrServers = 12;
lambda = util*nbrServers;
mu = 1;



meanRT = SQFapprox(lambda, mu, nbrServers)