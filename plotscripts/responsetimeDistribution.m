clear; clc;

%% Loading data
dirstring = '../results/'; % Change this if directory is differently located

d = dir(dirstring);
dirs = [];
for i = 1:length(d)
    if d(i).isdir == 1
        dirs = [dirs i];
    end
end
d = d(dirs(3:end));
m = length(d);


%% Getting histogram and plotting
for i = 1:m
    path = strcat(dirstring, d(i).name, '/sim-server*-rt.csv');
    dd   = dir(path);
    n = length(dd);
    
    disp(d(i).name);
    disp('  * Replicas histograms');
    total_latencies = []; % Holding all the latencies for the load balancing algorithm
    
    for j=1:n
        p = strcat(dirstring, d(i).name, '/sim-server', num2str(j),'-rt.csv');
        A = load(p);
        latencies = A(:,3); % Getting the latencies
        
        f = figure(); % Creating a centered figure
        movegui(f,'center');
        hist(latencies);
        title(strcat(d(i).name, ': replica ', num2str(j)));
        total_latencies = [total_latencies; latencies];    
    end
    
    pause;
    disp('  * Aggregate histogram');
    f = figure();
    movegui(f,'center');
    hist(total_latencies);
    title(strcat(d(i).name, ': aggregate results over all ', num2str(j), ' replicas'));
    pause;
    close all;
    
end