%% Get the data
% Only read the data once to create the .mat file, as it takes very long
% time to do!

clc
clear all;

addpath('./functions')

if ~isfile('randomized_sync_vs_nonsync.mat')
    path = '../simulation-results/randomized-sync-vs-nonsync';
    tests = dir(path);
    tests(1:2) = [];
    
    m = length(tests);
    dataCell = cell(m, 6);
    
    for k = 1:m
        k
        dataCell{k, 1} = tests(k).name;
        descr =  read_description_file([path '/' tests(k).name '/' 'description.csv']);
        dataCell{k, 2} = descr;
        c_SQF_d = read_final_result_file([path '/' tests(k).name '/' 'clusterSQF-PS' '/' 'sim-final-results.csv']);
        dataCell{k, 3} = c_SQF_d;
        SQF_d = read_final_result_file([path '/' tests(k).name '/' 'SQF-PS' '/' 'sim-final-results.csv']);
        dataCell{k, 4} = SQF_d;
        c_r_d = read_final_result_file([path '/' tests(k).name '/' 'clusterRandom-PS' '/' 'sim-final-results.csv']);
        dataCell{k, 5} = c_r_d;
        r_d = read_final_result_file([path '/' tests(k).name '/' 'Random-PS' '/' 'sim-final-results.csv']);
        dataCell{k, 6} = r_d;
    end
    
    save('randomized_sync_vs_nonsync.mat', 'dataCell');
else
    tmp = load('randomized_sync_vs_nonsync.mat');
    dataCell = tmp.dataCell;
    m = length(dataCell);
end

%% Process the data
utils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];

resultCell = cell(length(utils), 4);

for j=1:length(resultCell)
    resultCell{j,1} = [];
    resultCell{j,2} = [];
    resultCell{j,3} = [];
    resultCell{j,4} = [];
end

for i = 1:m
    normalized_error_sqf = (dataCell{i, 4}.avgResponseTime)/dataCell{i, 3}.avgResponseTime;
    normalized_error_random = (dataCell{i, 6}.avgResponseTime)/dataCell{i, 5}.avgResponseTime;
    clone_error_sqf = dataCell{i, 4}.cloneStdCoeff;
    clone_error_random = dataCell{i, 6}.cloneStdCoeff;
    idx = find(abs(utils-dataCell{i, 2}.util)<1e-3);
    
    resultCell{idx, 1} = [resultCell{idx, 1}, normalized_error_sqf];
    resultCell{idx, 2} = [resultCell{idx, 2}, normalized_error_random];
    resultCell{idx, 3} = [resultCell{idx, 3}, clone_error_sqf];
    resultCell{idx, 4} = [resultCell{idx, 4}, clone_error_random];
end

avg_normalized_sqf_errors = zeros(length(utils), 1);
avg_normalized_random_errors = zeros(length(utils), 1);
avg_clone_sqf_errors = zeros(length(utils), 1);
avg_clone_random_errors = zeros(length(utils), 1);

conf_normalized_sqf_errors = zeros(length(utils), 4);
conf_normalized_random_errors = zeros(length(utils), 4);
conf_clone_sqf_errors = zeros(length(utils), 4);
conf_clone_random_errors = zeros(length(utils), 4);

for l=1:length(resultCell)
    avg_normalized_sqf_errors(l) = mean(resultCell{l, 1});
    avg_normalized_random_errors(l) = mean(resultCell{l, 2});
    avg_clone_sqf_errors(l) = mean(resultCell{l, 3});
    avg_clone_random_errors(l) = mean(resultCell{l, 4});
    
    tmp_conf = confint(resultCell{l, 1});
    tmp_vec = [utils(l), 0.0000, avg_normalized_sqf_errors(l), avg_normalized_sqf_errors(l)-tmp_conf(1)];
    conf_normalized_sqf_errors(l, :) = tmp_vec;
    tmp_conf = confint(resultCell{l, 2});
    tmp_vec = [utils(l), 0.0000, avg_normalized_random_errors(l), avg_normalized_random_errors(l)-tmp_conf(1)];
    conf_normalized_random_errors(l, :) = tmp_vec;
    tmp_conf = confint(resultCell{l, 3});
    tmp_vec = [utils(l), 0.0000, avg_clone_sqf_errors(l), avg_clone_sqf_errors(l)-tmp_conf(1)];
    conf_clone_sqf_errors(l, :) = tmp_vec;
    tmp_conf = confint(resultCell{l, 4});
    tmp_vec = [utils(l), 0.0000, avg_clone_random_errors(l), avg_clone_random_errors(l)-tmp_conf(1)];
    conf_clone_random_errors(l, :) = tmp_vec;
end

%% Write data to txt-files

fileID = fopen('../plots/data/randomized-sync-vs-nonsync/randomized_sqf_clone_confint.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',conf_clone_sqf_errors');
fclose(fileID);

fileID = fopen('../plots/data/randomized-sync-vs-nonsync/randomized_sqf_mean_confint.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',conf_normalized_sqf_errors');
fclose(fileID);

fileID = fopen('../plots/data/randomized-sync-vs-nonsync/randomized_random_clone_confint.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',conf_clone_random_errors');
fclose(fileID);

fileID = fopen('../plots/data/randomized-sync-vs-nonsync/randomized_random_mean_confint.txt','w');
fprintf(fileID,'%6.4f %6.4f %6.4f %6.4f\n',conf_normalized_random_errors');
fclose(fileID);



