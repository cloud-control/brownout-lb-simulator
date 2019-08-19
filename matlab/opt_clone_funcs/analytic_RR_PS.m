function [optSer, meanRT] = analytic_clusterRandom_PS(LAMBDA_FRAC, CLONES)
    % Calculate optimal clone number and corresponding service times. 
    % 
    % Round Robin load balancing over cloning clusters strategy for PS
    % discipline using G/G/1 - PS approximation through G/M/1

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
            
            % Calultate Er/M/1 statistics
            s = (1 + X_C2)/2 * X_M1;
            l =  arrivalRate; %ph / s
            ph = l*s; % 2 / (1 + X_C2);
            
            ph

            poly = [K*ph, -(1 + K*ph), zeros(1, K-1), 1];
            z0 = max(abs(roots(poly)));
            
            z0
            if z0 < 0.99
               error(['z0 less than 1!'])
            end
            
            % Representing infinity
            N = 1000;
            P = zeros(N, 1);
            
            P(1) = 1 - ph;
            for k = 2:N
                P(k) = ph*(z0^K - 1)*z0^(-(k-1)*K);
            end
            
            k = [0:N-1];
            avgN = sum(k.*P');
            W = avgN / l - s;

            meanRespTimes(i, j) = X_M1 + 2 / (1 + X_C2) * W;
            
        end
    end
    
    meanRespTimes(meanRespTimes < 0) = inf;
    [val, idx] = min(meanRespTimes, [], 2);
    
    optSer = CLONES(idx);
    meanRT = val;
    
end