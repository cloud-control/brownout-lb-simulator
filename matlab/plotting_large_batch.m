function X = plotting_large_batch(testData, analytic_optClone, analytic_meanRT, ...
    CLONES, LAMBDA_FRAC, MC_SIMS, fracs, suffix)

    sIdx = [2, 3, 4, 5, 6, 1];

    m = length(fracs)
    n = length(testData)-1

    optClone = zeros(n, MC_SIMS, m);
    meanRT = zeros(n, MC_SIMS, m);
    X = []

    optClone_theory = zeros(n, m);
    meanRT_theory = zeros(n, m);
    
    for k = 1:m
        for i = 1:n   
            optClone(i, :, k) = testData(i+1).minAvgRTSer(fracs(k), :);
            meanRT(i, :, k) = testData(i+1).minAvgRTVal(fracs(k), :);

            if k == 1
                X = [X, convertCharsToStrings(testData(i+1).testName)];
            end

            if ~isempty(intersect(analytic_optClone.keys(), testData(i+1).testName))
                tmp_optClone = analytic_optClone(testData(i+1).testName)
                tmp_meanRT = analytic_meanRT(testData(i+1).testName)

                optClone_theory(i, k) = tmp_optClone(fracs(k));
                meanRT_theory(i, k) = tmp_meanRT(fracs(k));
            end

        end
    end
    [~, idx] = sort(mean(meanRT(:, :, 1), 2));
    optClone = optClone(idx, :, :);
    meanRT = meanRT(idx, :, :);

    optClone_theory = optClone_theory(idx, :);
    meanRT_theory = meanRT_theory(idx, :);
    
    X = X(idx)

        
    figure()
    clf()
    for k = 1:m
        subplot(m, 2, 1 + (k-1)*2)
        hold on;
        boxplot(optClone(:,:,k)', X);
        plot(1:n, optClone_theory(:, k), 'go')
        title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(k))))
        yticks(CLONES)
        set(gca, 'yscale', 'log')
        ylim([0.8, 15])

        subplot(m, 2, 2 + (k-1)*2)
        hold on;
        boxplot(meanRT(:,:,k)', X)
        plot(1:n, meanRT_theory(:, k), 'go')
        title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(k))))
        %set(gca, 'yscale', 'log')
        ylim([0, 15])
    end
    
    
    for k = 1:m
        optClone_stats = gen_boxplot_stats(optClone(:,:,k));
        meanRT_stats = gen_boxplot_stats(meanRT(:,:,k));

        save(['dat_files/optClone_' num2str(k) suffix '.dat'], 'optClone_stats', '-ascii');
        save(['dat_files/meanRT_' num2str(k) suffix '.dat'], 'meanRT_stats', '-ascii');

        x = 1:n; y = optClone_theory(:, k);
        idx = y > 0;
        csvwrite(['dat_files/optClone_' num2str(k) '_theory' suffix '.csv'], ...
            [x(idx)', y(idx)])

        x = 1:n; y = meanRT_theory(:, k);
        idx = y > 0;
        csvwrite(['dat_files/meanRT_' num2str(k) '_theory' suffix '.csv'], ...
            [x(idx)', y(idx)])
    end
end

function stats = gen_boxplot_stats(X)
    n = size(X, 1);
    stats = [ [1:n]', quantile(X', [0.25, 0.5, 0.75])', max(X')', min(X')'];
end

