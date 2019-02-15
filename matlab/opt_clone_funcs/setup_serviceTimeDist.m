function [X_M1, X_M2, X_Var, X_C2] = setup_serviceTimeDist(clones)

    hyperMeanServiceTime = 1/4.7;
    hyperCoeff = 10;

    x = [1:12]';
    dollyCDF = zeros(12, 1);
    dollyPDF = zeros(12,1);
    
    dollyPDF(1) = 0.230; dollyPDF(2) = 0.140; dollyPDF(3) = 0.09;
    dollyPDF(4) = 0.03; dollyPDF(5) = 0.08; dollyPDF(6) = 0.10;
    dollyPDF(7) = 0.04; dollyPDF(8) = 0.140; dollyPDF(9) = 0.12;
    dollyPDF(10) = 0.021; dollyPDF(11) = 0.007; dollyPDF(12) = 0.002;

    dollyCDF(1) = 0.230;dollyCDF(2) = 0.370;dollyCDF(3) = 0.460;
    dollyCDF(4) = 0.490;dollyCDF(5) = 0.570;dollyCDF(6) = 0.670;
    dollyCDF(7) = 0.710;dollyCDF(8) = 0.850;dollyCDF(9) = 0.970;
    dollyCDF(10) = 0.991;dollyCDF(11) = 0.998; dollyCDF(12) = 1.000;

    
    % Calculate the min distribution
    minDollyCDF = 1 - (1 - dollyCDF).^clones;
    minDollyPDF = zeros(size(minDollyCDF));
    minDollyPDF(1) = minDollyCDF(1);
    for k=2:length(minDollyCDF)
        minDollyPDF(k) = minDollyCDF(k) - minDollyCDF(k-1);
    end

    dollyM1 = sum(x.*minDollyPDF);
    dollyM2 = sum((x.^2).*minDollyPDF);
    dollyVar = dollyM2 - dollyM1.^2;
    dollyC2 = dollyVar / dollyM1.^2; 

    % First and second moments of service time
    X_M1 = hyperMeanServiceTime * dollyM1;
    X_M2 = ((1 + hyperCoeff)*hyperMeanServiceTime.^2)*dollyM2;

    % Variance of service time
    X_Var = X_M2 - X_M1^2;
    X_C2 = X_Var / X_M1^2;
end

