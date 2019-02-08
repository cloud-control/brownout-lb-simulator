function meanRT = SQFapprox_fcfs(lambda, mu, K, Ca, Cs)
    
    p = lambda / (mu*K);
    ph = p*(Ca^2 + Cs^2) / (2 + p*(Ca^2 + Cs^2 - 2));
    
    A = 0;
    for n = 0:K-1
       tmp = (K*ph)^n/factorial(n) + (K*ph)^K/(factorial(K)*(1 - ph));
       A = A + tmp;
    end
    
    P = (K*ph)^K / (factorial(K)*(1-ph)*A);
    
    W = 1/mu * P / (1 - ph^K);
    meanRT = W + 1/mu;
end

