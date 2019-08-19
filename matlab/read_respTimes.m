function data = read_respTimes(basepath)
    strats = dir(basepath);
    strats(1:2) = [];

    m = length(strats);
    
    paths = cell(m, 1);
    for i = 1:m
        runs =  dir([basepath '/' strats(i).name]);
        runs(1:2) = [];
        n = length(runs);

        subpaths = cell(n,1);
        for j = 1:n
            subpaths{j} = [basepath '/' strats(i).name  '/sim' num2str(j-1) ...
                '/sim-lb-allReqs.csv'];
        end

        paths{i} = subpaths;
    end

    data = read_paths(paths, strats);
end

function [data] = read_paths(paths, strats)
    m = size(paths, 1);
    n = size(paths{1}, 1);
    data = cell(m, size(paths{1}, 1)+1);
    
    for i = 1:m
        for k = 1:n
            table = readtable(paths{i}{k}, 'Delimiter', ',');
            data{i, k+1} = table.Var1;
            
        end
        data{i, 1} = strats(i).name;
    end
end


