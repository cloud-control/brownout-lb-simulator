function meanRT = SQFapprox_ps(lambda, mu, K)
K;
lambda;
mu;
util = lambda/(K*mu);

if util >=0.95
    
    meanRT = NaN;
else

    N = 1000; % represents infinity

    c3 = -0.29; c2 = 0.8822; c1 = -0.5349; c0 = 1.0112; c21 = -0.1864; c11 = 1.195; c01 = -0.016;
    u_p = c3*util^3 + c2*util^2 + c1*util + c0;
    v_p = c21*util^2 + c11*util + c01;
    a_p = util/(1-util);
    b_p = (-0.0263*util^2+0.0054*util+0.1155)/(util^2-1.939*util+0.9534);
    c_p = -6.2973*util^4+14.3382*util^3-12.3532*util^2+6.2557*util-1.005;
    d_p = (-226.1839*util^2+342.3814*util+10.2851)/(util^3-146.2751*util^2-481.1256*util+599.9166);
    e_p = 0.4462*util^3-1.8317*util^2+2.4376*util-0.0512;

    l_0 = mu*(a_p - b_p*c_p^K - d_p*e_p^K);
    l_2 = mu*(u_p*v_p^K);
    l_1 = mu*((mu/l_0)*((util-util^(K+1))/(1-util))+util^K-1)/(1+(l_2/mu)-util^K);

    l_vec = zeros(N,1);

    l_vec(1) = l_0;
    l_vec(2) = l_1;
    l_vec(3) = l_2;

    for n = 4:N
        l_vec(n) = util^K*mu;
    end

    prodsum = 0;
    for k = 1:N
        prod = 1;
        for i = 0:(k-1)
            prod = prod*l_vec(i+1)/mu;
        end

        prodsum = prodsum + prod;          
    end

    p_0 = 1/(1 + prodsum);

    p_vec = zeros(N,1);

    p_vec(1) = p_0;

    for l = 2:N
        p_vec(l) = p_vec(l-1)*l_vec(l-1)/mu;
    end
    k = [1:N]';

    avgQueue = sum((k-1).*p_vec);

    meanRT = avgQueue/(lambda/K);
end