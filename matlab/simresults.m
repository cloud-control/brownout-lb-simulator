%% Round Robin + Cloning Hyperexp+Dolly service times, Poisson arrivals

% 10 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR10 = [17.323, 33.222, 3.430, 11.673, 343.192];

% 11 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR11 = [17.545, 9.025, 2.956, 11.392, 5.501, 43.619];

% 12 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR12 = [17.876, 33.6970, 55.1049, 117.0940, 9.1370, 819.140];

% 13 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR13 = [20.675, 8.596, 3.576, 7.066, 8.9653, 284.689];

% 15 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR15 = [18.813, 9.4611, 26.350, 3.761, 430.242];

% 17 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR17 = [17.661, 8.646, 3.004, 1.753, 4.139, 51.177];
resultsrandom17 = [18.375, 4.034, 1.966, 1.397, 1.800, 8.212];

% 24 servers, arrival rate = 0.7*nbrServers, avg response times
resultsRR24 = [17.270, 39.155, 60.948, 155.947, 3.508, 825.106, 194.720];

plot(resultsRR10, 'x')
hold on;
plot(resultsRR11, 'x')
plot(resultsRR12, 'x')
plot(resultsRR13, 'x')