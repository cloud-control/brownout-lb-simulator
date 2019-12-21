function new_data = compresser(orig_data)

prev_y = 0.0;

new_index = 1;

new_data(1, 1) = orig_data(1, 1);
new_data(1, 2) = orig_data(1, 2);

for i = 2:(length(orig_data(:,2))-1)
    x_val = orig_data(i,1);
    y_val = orig_data(i,2);
    
    if (y_val-prev_y) > 0.005
        new_data(new_index, 1) = x_val;
        new_data(new_index, 2) = y_val;
        new_index = new_index + 1;
        prev_y = y_val;
    end
end

new_data(new_index, 1) = orig_data(end, 1);
new_data(new_index, 2) = orig_data(end, 2);


end