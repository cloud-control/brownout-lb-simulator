function X = plotting_large_batch(testData, analytic_optClone, analytic_meanRT, ...
    CLONES, LAMBDA_FRAC, MC_SIMS, suffix)

    fracs = [2, 4]
    sIdx = [2, 3, 4, 5, 6, 1];

    n = length(testData)-1

    optClone = zeros(n, MC_SIMS, 2);
    meanRT = zeros(n, MC_SIMS, 2);
    X = []

    optClone_theory = zeros(n, 2);
    meanRT_theory = zeros(n, 2);
    
    for i = 1:n   
        optClone(i, :, 1) = testData(i+1).minAvgRTSer(fracs(1), :);
        optClone(i, :, 2) = testData(i+1).minAvgRTSer(fracs(2), :);
        
        meanRT(i, :, 1) = testData(i+1).minAvgRTVal(fracs(1), :);
        meanRT(i, :, 2) = testData(i+1).minAvgRTVal(fracs(2), :);
        
        X = [X, convertCharsToStrings(testData(i+1).testName)];

        if ~isempty(intersect(analytic_optClone.keys(), testData(i+1).testName))
            tmp_optClone = analytic_optClone(testData(i+1).testName)
            tmp_meanRT = analytic_meanRT(testData(i+1).testName)
            
            optClone_theory(i, 1) = tmp_optClone(fracs(1));
            optClone_theory(i, 2) = tmp_optClone(fracs(2));
           
            meanRT_theory(i, 1) = tmp_meanRT(fracs(1));
            meanRT_theory(i, 2) = tmp_meanRT(fracs(2));
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
    subplot(2, 2, 1)
    hold on;
    boxplot(optClone(:,:,1)', X);
    plot(1:n, optClone_theory(:, 1), 'go')
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(1))))
    yticks(CLONES)
    set(gca, 'yscale', 'log')
    ylim([0.8, 15])
    
    subplot(2, 2, 2)
    hold on;
    boxplot(meanRT(:,:,1)', X)
    plot(1:n, meanRT_theory(:, 1), 'go')
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(1))))
    set(gca, 'yscale', 'log')
    
    subplot(2, 2, 3)
    hold on;
    boxplot(optClone(:,:,2)', X);
    plot(1:n, optClone_theory(:, 2), 'go')
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(2))))
    yticks(CLONES)
    set(gca, 'yscale', 'log')
    ylim([0.8, 15])
    
    subplot(2, 2, 4)
    hold on;
    boxplot(meanRT(:,:,2)', X)
    plot(1:n, meanRT_theory(:, 2), 'go')
    title(sprintf("Using %s %.2f","\lambda_{frac} = " , LAMBDA_FRAC(fracs(2))))
    set(gca, 'yscale', 'log')
    
    
    optClone_1 = gen_boxplot_stats(optClone(:,:,1));
    optClone_2 = gen_boxplot_stats(optClone(:,:,2));
    
    meanRT_1 = gen_boxplot_stats(meanRT(:,:,1));
    meanRT_2 = gen_boxplot_stats(meanRT(:,:,2));
    
    save(['dat_files/optClone_1' suffix '.dat'], 'optClone_1', '-ascii');
    save(['dat_files/optClone_2' suffix '.dat'], 'optClone_2', '-ascii');
    
    save(['dat_files/meanRT_1' suffix '.dat'], 'meanRT_1', '-ascii');
    save(['dat_files/meanRT_2' suffix '.dat'], 'meanRT_2', '-ascii');
    
    x = 1:n; y = optClone_theory(:, 1);
    idx = y > 0;
    csvwrite(['dat_files/optClone_1_theory' suffix '.csv'], [x(idx)', y(idx)])
    
    x = 1:n; y = optClone_theory(:, 2);
    idx = y > 0;
    csvwrite(['dat_files/optClone_2_theory' suffix '.csv'], [x(idx)', y(idx)]) 
    
    x = 1:n; y = meanRT_theory(:, 1);
    idx = y > 0;
    csvwrite(['dat_files/meanRT_1_theory' suffix '.csv'], [x(idx)', y(idx)])
    
    x = 1:n; y = meanRT_theory(:, 2);
    idx = y > 0;
    csvwrite(['dat_files/meanRT_2_theory' suffix '.csv'], [x(idx)', y(idx)])

    %boxplotsstats = [[0 0 1 1 2 2 3 3 4]', quantile(Y', [0.25, 0.5, 0.75])', max(Y')', min(Y')'];
    %save csvfiles/boxplot_example.dat boxplotsstats  -ascii
    %save csvfiles/boxplot_example_truth.dat Y_theory  -ascii



  

    
end

function stats = gen_boxplot_stats(X)
    n = size(X, 1);
    stats = [ [1:n]', quantile(X', [0.25, 0.5, 0.75])', max(X')', min(X')'];
end

