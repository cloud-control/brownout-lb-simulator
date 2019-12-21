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
            subpaths{j} = [basepath '/' strats(i).name  '/sim' num2str(j-1) ...
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
        i
        n = size(paths{i}, 1);
        for j = 1:n 
            fileID = fopen(paths{i}{j});
            C = textscan(fileID, '%s', 'Delimiter', '\n');
            fclose(fileID);
            

            names = cellfun(@(x) strrep(x, ' ', ''), strsplit(C{1}{1}, ','), ...
                'UniformOutput', false);
            vals = cellfun(@(x) strrep(x, ' ', ''), strsplit(C{1}{2}, ','), ...
                'UniformOutput', false);

            t = cell2table(vals);
            t.Properties.VariableNames = names;
            if isempty(data{i, 1})
                data{i, 1} = t;
            else
                data{i, 1} = [data{i, 1}; t];
            end
        end
        data{i, 2} = strats(i).name;
    end
end

