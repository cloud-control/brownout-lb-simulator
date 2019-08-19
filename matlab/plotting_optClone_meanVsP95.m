function [X, fit] = plotting_large_batch(testData, CLONES, LAMBDA_FRAC, MC_SIMS, fracs)

    sIdx = [2, 3, 4, 5, 6, 1];

    m = length(fracs)
    n = length(testData)-1

    optClone_mean = zeros(n, MC_SIMS, m);
    optClone_p95 = zeros(n, MC_SIMS, m);
    
    meanRT = zeros(n, MC_SIMS, m);
    p95RT = zeros(n, MC_SIMS, m);
    X = []
    
    for k = 1:m
        for i = 1:n   
            optClone_mean(i, :, k) = testData(i+1).minAvgRTSer(fracs(k), :);
            optClone_p95(i, :, k) = testData(i+1).minP95RTSer(fracs(k), :);
            
            meanRT(i, :, k) = testData(i+1).minAvgRTVal(fracs(k), :);
            p95RT(i, :, k) = testData(i+1).minP95RTVal(fracs(k), :);

            if k == 1
                X = [X, convertCharsToStrings(testData(i+1).testName)];
            end
        end
    end
        
    figure()
    clf()
    for k = 1:m
        subplot(m, 1, 1 + (k-1))
        hold on;
        plot(optClone_mean(:,:,k), 'bo');
        plot(optClone_p95(:,:,k), 'rx');
        xticks(1:n)
        xticklabels(cellstr(X))
        title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(k))))
        yticks(CLONES)
        set(gca, 'yscale', 'log')
        xlim([0, n+1])
        ylim([0.8, 15])
    end
    
    %numerical comp
    fit = zeros(m, n);
    for k = 1:m
        vals_mean = zeros(n, length(CLONES));
        vals_p95 = zeros(n, length(CLONES));
        for i = 1:length(CLONES)
            vals_mean(:, i) = sum(optClone_mean(:,:,k) == CLONES(i), 2)
            vals_p95(:, i) = sum(optClone_p95(:,:,k) == CLONES(i), 2)
        end
        
        testval = MC_SIMS * ones(n, 1)
        if sum(vals_mean, 2) ~= testval || sum(vals_p95, 2) ~= testval
            error("Total amount of hits wrong")
        end
        
        fit(k, :) = abs(sum(vals_mean - vals_p95, 2)) / MC_SIMS;
    end

end


