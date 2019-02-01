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

