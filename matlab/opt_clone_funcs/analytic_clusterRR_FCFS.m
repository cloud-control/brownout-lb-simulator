function [optSer, meanRT] = analytic_clusterRandom_FCFS(LAMBDA_FRAC, CLONES)
    % Calculate optimal clone number and corresponding service times. 
    % 
    % Round Robin load balancing over cloning clusters strategy for FCFS 
    % discipline using Kingmans G/G/1 approximation. 

    SERVERS = 12;
    
    m = length(LAMBDA_FRAC);
    n = length(CLONES);
    
    meanRespTimes = zeros(m, n);
    utils = zeros(m, n);

    for i = 1:m
        for j = 1:n
            
            K = SERVERS / CLONES(j);
            arrivalRate = SERVERS*LAMBDA_FRAC(i)/K;
            
            %Assuming Erlang input
            Y_C2 = 1/K;
            
            [X_M1, X_M2, X_Var, X_C2] = setup_serviceTimeDist(CLONES(j));
            
            utils(i,j) =  arrivalRate * X_M1;
            
            p = utils(i, j);           

            meanRespTimes(i, j) = X_M1 + X_M1*p / (1-p) * (X_C2 + Y_C2)/2;
            
        end
    end
    
    meanRespTimes(meanRespTimes < 0) = inf;
    [val, idx] = min(meanRespTimes, [], 2);
    
    optSer = CLONES(idx);
    meanRT = val;
    
end