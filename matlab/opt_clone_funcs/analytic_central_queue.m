function [optSer, meanRT] = analytic_central_queue(LAMBDA_FRAC, CLONES)
    % Calculate optimal clone number and corresponding service times. 
    % 
    % Central Queue strategy for FCFS discipline using M/G/K
    % approximation.

  
    
    SERVERS = 12;
    
    m = length(LAMBDA_FRAC);
    n = length(CLONES);
    
    meanRespTimes = zeros(m, n);
    utils = zeros(m, n);

    for i = 1:m
        arrivalRate = SERVERS*LAMBDA_FRAC(i);
        for j = 1:n
            
            K = SERVERS / CLONES(j);
            [X_M1, X_M2, X_Var, X_C2] = setup_serviceTimeDist(CLONES(j));
            
            utils(i,j) =  arrivalRate * X_M1 / K;
            
            p = utils(i, j);           
            % Calculate M/M/k waiting time
            p0 = (K*p)^K/factorial(K)*1/(1-p);
            for k = 0:(K-1)
               p0 = p0 + (K*p)^k / factorial(k); 
            end
            p0 = 1/p0;
            pQ = (K*p)^K / factorial(K) * p0 / (1-p);
            eW_mmk = pQ * p / (arrivalRate * (1-p));

            meanRespTimes(i, j) = X_M1 + X_M2/(2*X_M1^2)*eW_mmk;
            
        end
    end
    
    meanRespTimes(meanRespTimes < 0) = inf;
    [val, idx] = min(meanRespTimes, [], 2);
    
    optSer = CLONES(idx);
    meanRT = val;
    
end

