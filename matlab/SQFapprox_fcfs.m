function meanRT = SQFapprox_fcfs(lambda, mu, K, Ca, Cs)
    
    p = lambda / (mu*K);
    
    % G/G/1
    %ph = p*(Ca^2 + Cs^2) / (2 + p*(Ca^2 + Cs^2 - 2));
    
    % M/G/1
    ph = p*(1+Cs^2) / (2 + p*(Cs^2-1));
    
    A = (K*ph)^K/(factorial(K)*(1 - ph));
    for n = 0:K-1
       A = A + (K*ph)^n/factorial(n);
    end
    
    P = (K*ph)^K / (factorial(K)*(1-ph)*A);
    
    W = 1/mu * P / (1 - ph^K);
    meanRT = W + 1/mu;
end

