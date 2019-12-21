function data = read_combined_description_file(filepath)

tmp = readtable(filepath);

dist_tmp = tmp.Properties.VariableNames(2);
dist = dist_tmp{1};

values = tmp.(2);
util = values(1);
nbrServer = values(2);
cloneFactor = values(3);
meanServiceTime = values(4);
lambdaFrac = values(5);
delayFrac = values(6);
arrivalDelay = values(7);
cancellationDelayFrac = values(8);
cancellationDelay = values(9);

data.dist = dist;
data.util = util;
data.nbrServer = nbrServer;
data.cloneFactor = cloneFactor;
data.meanServiceTime = meanServiceTime;
data.lambdaFrac = lambdaFrac;
data.delayFrac = delayFrac;
data.arrivalDelay = arrivalDelay;
data.cancellationDelayFrac = cancellationDelayFrac;
data.cancellationDelay = cancellationDelay;
end