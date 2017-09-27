%% IAE

responsetimesff(responsetimesff == 0.0) = NaN;

IAE = nansum(abs(responsetimesff-ones(size(responsetimesff))));

%% variances


var = nanvar(optionalTimesff)

%% maximum values

max = nanmax(optionalTimesff)


%% optional content

allreq = 287720;

optionalpercentage = length(optionalTimesmm) / allreq