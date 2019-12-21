%% Get the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!
clc
clear all;

addpath('./functions')

if ~isfile('randomized_cancellation_data.mat')
    path = '../simulation-results/randomized-cancellation-delays';
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 3);
    
    for k = 1:m
        k
        dataCell{k, 1} = tests(k).name;
        descr =  read_cancellation_description_file([path '/' tests(k).name '/' 'description.csv']);
        dataCell{k, 2} = descr;
        result = read_final_result_file([path '/' tests(k).name '/' 'sim-final-results.csv']);
        dataCell{k, 3} = result;
    end
    
    save('randomized_cancellation_data.mat', 'dataCell');
    
else
    tmp = load('randomized_cancellation_data.mat');
    dataCell = tmp.dataCell;
    m = length(dataCell);
 end

%% Save data


%% Process the data
utils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];
delayFracs = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5];

resultCell = cell(length(delayFracs), 2);

for j=1:length(resultCell)
    resultCell{j,1} = [];
end

for i = 1:m
    if dataCell{i, 2}.cancellationDelayFrac < 0.007
        continue
    end
    mu = 1/(dataCell{i, 2}.meanServiceTime);
    mu_bound = 1/(dataCell{i, 2}.meanServiceTime + dataCell{i, 2}.cancellationDelay);
    theroetical_respTime = 1/(mu - dataCell{i, 2}.nbrServer*dataCell{i, 2}.lambdaFrac); 
    if theroetical_respTime < 0.0
        disp 'Error!'
    end
    
    if mu_bound > dataCell{i, 2}.nbrServer*dataCell{i, 2}.lambdaFrac
        bound = 1/(mu_bound - dataCell{i, 2}.nbrServer*dataCell{i, 2}.lambdaFrac);
    else
        bound = NaN;
    end
    
    responseTime = dataCell{i, 3}.avgResponseTime; 
    bound_error = bound/theroetical_respTime;
    resp_error = responseTime/theroetical_respTime;
    if (dataCell{i, 2}.nbrServer < 11)
        idx_util = find(abs(utils-dataCell{i, 2}.util)<1e-5);
        idx_frac = find(abs(delayFracs-dataCell{i, 2}.cancellationDelayFrac)<1e-5);
        resultCell{idx_frac, 1} = [resultCell{idx_frac, 1}, bound_error];
        resultCell{idx_frac, 2} = [resultCell{idx_frac, 2}, resp_error];
    end     
end

avg_bound_errors = zeros(length(delayFracs), 1);
avg_resp_errors = zeros(length(delayFracs), 1);

conf_bound_errors = zeros(length(delayFracs), 4);
conf_resp_errors = zeros(length(delayFracs), 4);

for l=1:length(resultCell)
    
    avg_bound_errors(l) = nanmean(resultCell{l, 1});
    avg_resp_errors(l) = mean(resultCell{l, 2});
    
    tmp_conf = confint(resultCell{l, 1});
    
    if sum(isnan(resultCell{l, 1})) >= 1
        avg_bound_errors(l) = (10 - tmp_conf(1))/2 + tmp_conf(1);
    end
    
    tmp_vec = [delayFracs(l), 0.0000, avg_bound_errors(l), avg_bound_errors(l)-tmp_conf(1)];
    conf_bound_errors(l, :) = tmp_vec;
    
    tmp_conf = confint(resultCell{l, 2});
    tmp_vec = [delayFracs(l), 0.0000, avg_resp_errors(l), avg_resp_errors(l)-tmp_conf(1)];
    conf_resp_errors(l, :) = tmp_vec;
end

%% Write data to txt-files

fileID = fopen('../plots/data/randomized-delays/randomized_cancellation_delays_confint_bound.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',(conf_bound_errors(1:end, :))');
fclose(fileID);

fileID = fopen('../plots/data/randomized-delays/randomized_cancellation_delays_confint_resp.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',(conf_resp_errors(1:end, :))');
fclose(fileID);




