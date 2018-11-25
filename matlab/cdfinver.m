function icdf = cdfinver(x_s, cdfer, cdf_goal)

    N = length(x_s);

    x_u = N;
    x_l = 1;
    x_i = floor((x_u - x_l) / 10);
    
    x_i_prev = -1;

    while x_i ~= x_i_prev

        if cdfer(x_i) > cdf_goal
            x_u = x_i;
        elseif cdfer(x_i) < cdf_goal
            x_l = x_i;
        end
        
        x_i_prev = x_i;
        x_i = floor((x_u - x_l) / 2) + x_l;
    end
    if x_u == x_l
        disp('ffs!');
    end
    total_diff = cdfer(x_u) - cdfer(x_l);
    diff = cdf_goal - cdfer(x_l);      
    
    if total_diff < 0.00001
        %disp('too small!')
        icdf = x_s(x_l);
    else
        icdf = x_s(x_l) + (diff/total_diff)*(x_s(x_u) - x_s(x_l));
    end  
end