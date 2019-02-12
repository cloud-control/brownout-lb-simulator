function data = read_data(basepath)
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
            subpaths{j} = [basepath '/' strats(i).name  '/run' num2str(j-1) ...
                '/sim-final-results.csv'];
        end

        paths{i} = subpaths;
    end

    data = read_paths(paths, strats);
end


function [data] = read_paths(paths, strats)
    m = size(paths, 1);
    data = cell(m, 2);
    
    for i = 1:m
        n = size(paths{i}, 1);
        for j = 1:n
            t = readtable(paths{i}{j}, 'Delimiter', ',');
            if isempty(data{i, 1})
                data{i, 1} = t;
            else
                data{i, 1} = [data{i, 1}; t];
            end
        end
        data{i, 2} = strats(i).name;
    end
end

