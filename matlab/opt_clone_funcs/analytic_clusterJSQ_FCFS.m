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
            
            if K > 1
                ph = p*(1+X_C2) / (2 + p*(X_C2-1));

                A = (K*ph)^K/(factorial(K)*(1 - ph));
                for k = 0:K-1
                   A = A + (K*ph)^k/factorial(k);
                end

                P = (K*ph)^K / (factorial(K)*(1-ph)*A);
                
                meanRT = X_M1 +  X_M1 * P / (1 - ph^K);
            else
                % If K = 1, then the server system is equivalent to M/G/1
                meanRT = X_M1 + p*X_M1*(1 + X_C2)/(2*(1-p));                      
            end
            
            meanRespTimes(i, j) = meanRT;
            
        end
    end
    
    meanRespTimes(meanRespTimes < 0) = inf;
    [val, idx] = min(meanRespTimes, [], 2);
    
    optSer = CLONES(idx);
    meanRT = val;
    
end