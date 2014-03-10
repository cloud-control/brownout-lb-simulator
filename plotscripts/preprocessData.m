clear; clc;

%% Loading data
dirstring = '../results/';

d = dir(dirstring);
dirs = [];
for i = 1:length(d)
    if d(i).isdir == 1
        dirs = [dirs i];
    end
end
d = d(dirs(3:end));

m = length(d);

for i = 1:m
    path = strcat(dirstring, d(i).name, '/sim-server*-rt.csv');
    dd   = dir(path);
    n = length(dd);
    
    avg_latencies = [];
    max_latencies = [];
    dimmers       = [];
    utilization   = [];
    for j=1:n
        p = strcat(dirstring, d(i).name, '/sim-server', num2str(j),'.csv');
        A=load(p);
        
        t             = A(:,1);
        avg_latencies = [avg_latencies A(:,2)];
        max_latencies = [max_latencies A(:,3)];
        dimmers       = [dimmers A(:,4)];
        utilization   = [utilization A(:,5)];
    
    end
    data(i).name = d(i).name;
    data(i).t    = t;
    data(i).avg_latencies = avg_latencies;
    data(i).max_latencies = max_latencies;
    data(i).dimmers       = dimmers;
    data(i).utilization   = utilization;
    
    path2 = [dirstring, d(i).name, '/sim-final-results.csv'];
    performance = csvread(path2,0,1);
    data(i).performance = performance;
end



save('data.mat','data');
