function [optSer, meanRT] = analytic_clusterRandom_FCFS(LAMBDA_FRAC, CLONES)
    % Calculate optimal clone number and corresponding service times. 
    % 
    % JSQ load balancing over cloning clusters strategy for FCFS 
    % discipline using Nelsson93 formula

    SERVERS = 12;
    
    m = length(LAMBDA_FRAC);
    n = length(CLONES);
    
    meanRespTimes = zeros(m, n);
    utils = zeros(m, n);

    for i = 1:m
        for j = 1:n
            
            K = SERVERS / CLONES(j);
            arrivalRate = SERVERS*LAMBDA_FRAC(i);
            
            [X_M1, X_M2, X_Var, X_C2] = setup_serviceTimeDist(CLONES(j));
            
            utils(i,j) =  arrivalRate * X_M1 / K;
            
            p = utils(i, j);

            N = 1000; % represents infinity
            
            c3 = -0.29; c2 = 0.8822; c1 = -0.5349; c0 = 1.0112; c21 = -0.1864; c11 = 1.195; c01 = -0.016;
            u_p = c3*p^3 + c2*p^2 + c1*p + c0;
            v_p = c21*p^2 + c11*p + c01;
            a_p = p/(1-p);
            b_p = (-0.0263*p^2 + 0.0054*p + 0.1155) / (p^2 - 1.939*p + 0.9534);
            c_p = -6.2973*p^4 + 14.3382*p^3 - 12.3532*p^2 + 6.2557*p - 1.005;
            d_p = (-226.1839*p^2 + 342.3814*p + 10.2851) ... 
                / (p^3 - 146.2751*p^2 - 481.1256*p + 599.9166);
            e_p = 0.4462*p^3 - 1.8317*p^2 + 2.4376*p - 0.0512;

            l_0 = 1/X_M1 * (a_p - b_p*c_p^K - d_p*e_p^K);
            l_2 = 1/X_M1 * (u_p*v_p^K);
            l_1 = 1/X_M1 * ((1/(X_M1*l_0))*((p - p^(K+1)) / (1 - p)) + p^K-1) ...
                / (1 + (l_2*X_M1) - p^K);

            l_vec = zeros(N,1);

            l_vec(1) = l_0;
            l_vec(2) = l_1;
            l_vec(3) = l_2;

            for l = 4:N
                l_vec(l) = p^K / X_M1;
            end

            prodsum = 0;
            for l = 1:N
                prod = 1;
                for h = 0:(l-1)
                    prod = prod*l_vec(h+1) * X_M1;
                end

                prodsum = prodsum + prod;          
            end

            p_0 = 1/(1 + prodsum);

            p_vec = zeros(N,1);

            p_vec(1) = p_0;

            for l = 2:N
                p_vec(l) = p_vec(l-1)*l_vec(l-1) * X_M1;
            end
            k = [1:N]';

            avgQueue = sum((k-1).*p_vec);
            meanRespTimes(i, j) = avgQueue/(arrivalRate/K);
            
        end
    end
    
    meanRespTimes(meanRespTimes < 0) = inf;
    [val, idx] = min(meanRespTimes, [], 2);
    
    optSer = CLONES(idx);
    meanRT = val;
    
end