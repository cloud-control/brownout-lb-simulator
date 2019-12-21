function data = read_description_file(filepath)

tmp = readtable(filepath);

dist_tmp = tmp.Properties.VariableNames(2);
dist = dist_tmp{1};

values = tmp.(2);
util = values(1);
nbrServer = values(2);
cloneFactor = values(3);
lambdaFrac = values(4);

data.dist = dist;
data.util = util;
data.nbrServer = nbrServer;
data.cloneFactor = cloneFactor;
data.lambdaFrac = lambdaFrac;
end