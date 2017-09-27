fname='delcomp_ec_control_2015-09-23_09-40-12.log';
upper=3504+120;
lower=14;

%%
fname='delcomp_ec_control_2015-09-23_12-29-05.log';
upper=3492+120;
lower=3;

%%
fname='delcomp_ec_control_2016-10-18_01-31-16.log';
upper=1e9;
lower=3;

%%
fname='delcomp_ec_control_2016-10-19_13-43-14.log';
upper=1e9;
lower=40+2470+1500;

%%
fname='delcomp_ec_control_2016-10-19_15-02-36.log';
upper=1e9;
lower=1800;

%%
fname='delcomp_ec_control_2016-10-21_11-40-05.log';
upper=1e9;
lower=0;

%%
fname='delcomp_ec_control_2016-10-21_13-10-48.log';
upper=1109+1200;
lower=1109;

%%
fname='delcomp_ec_control_2016-10-21_14-17-15.log';
upper=1200;
lower=0;

%%
fname='delcomp_ec_control_2016-10-21_14-51-31.log';
upper=1200;
lower=0;

%%
% New, slower (better) model
fname='delcomp_ec_control_2016-10-21_16-34-31.log';
upper=1e9;
lower=0;

%%
% First one with consective downscale protection
fname='delcomp_ec_control_2016-10-21_17-23-45.log';
upper=1e9;
lower=0;

%%
% Long one with consective downscale protection
fname='delcomp_ec_control_2016-10-22_12-54-06.log';
upper=1e9;
lower=0;

%%
% Consective downscale protection and slower loop
fname='delcomp_ec_control_2016-10-24_09-18-07.log';
upper=1200;
lower=0;

%%
% First test with h=5
fname='delcomp_ec_control_2016-10-24_11-00-53.log';
upper=1e9;
lower=0;

%%
% First test with h=2
fname='delcomp_ec_control_2016-10-24_16-39-39.log';
upper=1200;
lower=0;

%%
% First test with threshold+cooldown
fname='delcomp_ec_control_2016-10-24_17-31-49.log';
upper=1200;
lower=0;

%%
% Threshold with smaller step. Should be bad
fname='delcomp_ec_control_2016-10-25_12-52-02.log';
upper=1200;
lower=0;

%%
% Lambda-tuned PI
fname='delcomp_ec_control_2016-10-27_16-10-23.log';
upper=1e9;
lower=0;

%%
% Compensated PI with h=2, poles in p, 0.9. Consecutive downscale protection
fname='delcomp_ec_control_2016-11-01_14-03-12.log';
upper=1200;
lower=0;

%%
% Compensated PI with h=2, poles in p, 0.9. No downscale protection
fname='delcomp_ec_control_2016-11-01_20-37-02.log';
upper=1200;
lower=0;

%%
% Compensated PI with h=2, poles in p, 0.9. No downscale protection
% This is figure stepfast1 in IFAC17
fname='delcomp_ec_control_2016-11-01_20-37-02.log';
upper=570;
lower=270;

%%
% Compensated PI with h=2, poles in p, 0.95. No downscale protection
fname='delcomp_ec_control_2016-11-02_14-26-43.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.95. No downscale protection
% This is figure stepslow1 in IFAC17
fname='delcomp_ec_control_2016-11-02_14-26-43.log';
lower=1456;
upper=1758;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
fname='delcomp_ec_control_2016-11-02_15-18-00.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% Long experiment!
fname='delcomp_ec_control_2016-11-14_01-05-50.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% New full-minute downscale protocol
fname='delcomp_ec_control_2016-11-14_16-13-55.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% Slower pole from sysid toolbox
fname='delcomp_ec_control_2016-11-17_08-53-39.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75
fname='delcomp_ec_control_2016-11-17_09-24-41.log';
lower=0;
upper=1e9;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. Real shutdowns and startups (git+nginx rebuild)!
fname='delcomp_ec_control_2016-11-17_11-28-16.log';
lower=0;
upper=1200;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. Real shutdowns and startups and warmup. New system with
% HostMaintainer
fname='delcomp_ec_control_2016-11-22_14-35-03.log';
lower=0;
upper=1200;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. NOT real shutdowns and startups and warmup. New system with
% HostMaintainer
fname='delcomp_ec_control_2016-11-22_15-12-32.log';
lower=0;
upper=1200;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. NOT real shutdowns and startups and warmup. New system with
% HostMaintainer
fname='delcomp_ec_control_2016-11-22_16-36-58.log';
lower=0;
upper=1200*6;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. Real shutdowns and startups and warmup. New system with
% HostMaintainer
fname='delcomp_ec_control_2016-11-28_13-06-45.log';
lower=0;
upper=1200*3;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. NOT real shutdowns and startups and warmup. New system with
% HostMaintainer
fname='delcomp_ec_control_2016-11-29_09-39-30.log';
lower=0;
upper=1200*3;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. NOT real shutdowns and startups and warmup. New system with
% HostMaintainer
% This is stepfast2
fname='delcomp_ec_control_2016-11-29_09-39-30.log';
lower=2948+50;
upper=lower+300;

%%
% Compensated PI with h=2, poles in p, 0.925. No downscale protection
% p=0.75. NOT real shutdowns and startups and warmup. New system with
% HostMaintainer

% Long experiment with periodic steps up and down!
fname='delcomp_ec_control_2016-11-29_17-16-53.log';
lower=94;
upper=1e9;

%%
disp(['Loading from ' fname]);
d=load(fname);

show_load = 1;

factor=5;
e = zeros(floor(size(d, 1)/factor), size(d, 2));
for ei=1:size(e,1)
    e(ei, :) = mean(d((factor*(ei-1)+1):(factor*ei), :), 1);
end
%d=e;

disp('Fixing data');
d(:,1) = (d(:,1)-min(d(:,1))) ./ 1000;
d=d((d(:,1)<upper&d(:,1)>lower), :);
d(:,1) = (d(:,1)-min(d(:,1)));
disp('Done');

%
%
figure(112);
clf
a=[];

a(end+1)=subplot(211+100*show_load);
ref=0.25;
cla
hold all;
if size(d, 2) > 12
    stairs(d(:,1), d(:,14))
    stairs(d(:,1), d(:,4));
    stairs(d(:,1), d(:,5));
    stairs(d(:,1), d(:,13));
    stairs([min(d(:,1)) max(d(:,1))], [ref ref], '--');
    legend('Mean RT', 'Delayed', 'Delay-free', 'Compensated', 'Ref', 'Location', 'NorthEast')
else
    stairs(d(:,1), d(:,6))
    stairs(d(:,1), d(:,4));
    stairs(d(:,1), d(:,5));
    stairs(d(:,1), d(:,2));
    stairs([min(d(:,1)) max(d(:,1))], [ref ref], '--');
    legend('Filtered RT', 'Delayed', 'Delay-free', 'Filtered Compensated', 'Ref', 'Location', 'NorthEast')
end
hold off
grid on
ylabel('Response times (s)');

% hhh=figure;
% copyobj(a(1), hhh);
% set(hhh, 'Position','default');
% figure(112)

a(end+1)=subplot(212+100*show_load);
cla; hold all
%plot(d(:,1), d(:,8), d(:,1), d(:,9), d(:,1), d(:,9)+d(:,10), '--');
stairs(d(:,1), d(:,8));
stairs(d(:,1), d(:,9));
stairs(d(:,1), d(:,9)+d(:,10), '--');
legend('m', 'm_r', 'm_b', 'Location', 'SouthEast');
grid on
ylabel('Machines');

if show_load
    a(end+1)=subplot(313);
    %plot(d(:,1), d(:,3)./d(:,8)); ylabel('Clients/machine');
    stairs(d(:,1), d(:,3)); ylabel('Clients');
    grid on
    xlabel('Time (s)');
    ylim(ylim+[-100 100])
end

linkaxes(a, 'x');

totalNewBootingMachines = sum(max(0, diff(d(:,9)+d(:,10))));
totalMachineSecondsUsed = sum(d(:,9)+d(:,10));

fprintf('totalNewBootingMachines=%d, totalMachineSecondsUsed=%d (per second=%.3f)\n', ...
    totalNewBootingMachines, totalMachineSecondsUsed, totalMachineSecondsUsed/max(d(:,1)));
fprintf('Mean process output signal=%.3f', mean(d(:, 14)));
if size(d, 2)>15
    fprintf(', mean response time=%.3f, ISE=%.3f\n', sum(d(:,14).*d(:,15))/sum(d(:,15)), sum(d(:,16).*d(:,15)));
else
    fprintf('\n');
end

extraaxisoptions='legend style={font=\tiny}';

filename = sprintf('%s.tikz', fname(1:end-4));
fprintf('Write to %s\n', filename);
matlab2tikz(filename, 'height', '\figureheight', 'width', '\figurewidth', 'showInfo', false, 'extraaxisoptions', extraaxisoptions);

%%
from=d(1,3);
for i=2:length(d(:,3))
    if d(i,3) ~= from
        to=d(i,3);
        first = i;
        break
    end
end
for i=i+1:length(d(:,3))
    if d(i,3)==from && d(i+1,3)==to
        second = i+1;
        break
    end
end
period = d(second,1)-d(first,1);

maxi=floor(max(d(:,1))/period-2);
for i=0:maxi
    fprintf('Showing %d/%d\n', i, maxi)
    xlim([0 2*period]+i*period)
    if i~=maxi
        pause
    end
end

%% Make periodic plots
disp(['Loading from ' fname]);
d=load(fname);

disp('Fixing data');
d(:,1) = (d(:,1)-min(d(:,1))) ./ 1000;
d=d((d(:,1)<upper&d(:,1)>lower+1*period), :);
d(:,1) = (d(:,1)-min(d(:,1)));
disp('Done');

period = 600;

figure(2)
hold all
ts = unique(round(mod(d(:,1), period)));
ds = zeros(size(ts, 1), size(d, 2));
dd = zeros(size(ts, 1), size(d, 2));
dmax = zeros(size(ts, 1), size(d, 2));
dmin = zeros(size(ts, 1), size(d, 2));
x = [];
g = [];
for i=1:length(ts)
    t = ts(i);
    cols = find(round(mod(d(:,1), period)) == t);
    ds(i, :) = mean(d(cols, :));
    dd(i, :) = std(d(cols, :));
    dmax(i, :) = max(d(cols, :));
    dmin(i, :) = min(d(cols, :));
    ds(i, 1) = t;
end

figure(2);
clf
% RT=14, Compensated=13, Delayed=4, Delayfree=5, m=8, m_r=9, m_b-m_r=10
cols = [14 13 8 9 10];
ylabs = {'Actual response times (s)', 'Compensated response times (s)',...
    'Control signal, m (1)', 'Runnings VMs (1)', 'Booting VMs (1)' };
hold all
for i=1:length(cols)
    col = cols(i);
    
    subplot(length(cols)*100+10+i);
    Y=[dmax(:, col)', fliplr(dmin(:, col)')];
    X=[ds(:, 1)', fliplr((ds(:, 1))')];
    fill(X, Y, 'c');
    hold all
    
    Y=[(ds(:, col) + dd(:, col))', fliplr((ds(:, col) - dd(:, col))')];
    X=[ds(:, 1)', fliplr((ds(:, 1))')];
    fill(X, Y, 'b');
    plot(ds(:, 1), ds(:, col), 'k', 'LineW', 2)
    if col==14 || col==13 || col==4 || col==5
        plot([min(ds(:, 1)) max(ds(:, 1))], 0.25+zeros(1, 2), 'r--', 'LineW', 1.5)
    end
    ylabel(ylabs{i})
    grid on

    if i==1
        title('Mean over 49 experiments (light blue min/max, dark blue \pm 1 stddev, black mean, dashed ref)');
    end
end
xlabel('Time (s)');


figure(113);
clf
a=[];

d = ds;

a(end+1)=subplot(211+100*show_load);
ref=0.25;
cla
hold all;
if size(d, 2) > 12
    stairs(d(:,1), d(:,14));
    stairs(d(:,1), d(:,4));
    stairs(d(:,1), d(:,5));
    stairs(d(:,1), d(:,13));
    stairs([min(d(:,1)) max(d(:,1))], [ref ref], '--');
    legend('Mean RT', 'Delayed', 'Delay-free', 'Compensated', 'Ref', 'Location', 'NorthEast')
else
    stairs(d(:,1), d(:,6))
    stairs(d(:,1), d(:,4));
    stairs(d(:,1), d(:,5));
    stairs(d(:,1), d(:,2));
    stairs([min(d(:,1)) max(d(:,1))], [ref ref], '--');
    legend('Filtered RT', 'Delayed', 'Delay-free', 'Filtered Compensated', 'Ref', 'Location', 'NorthEast')
end
hold off
grid on
ylabel('Response times (s)');

a(end+1)=subplot(212+100*show_load);
cla; hold all
stairs(d(:,1), d(:,8));
stairs(d(:,1), d(:,9));
stairs(d(:,1), d(:,9)+d(:,10), '--');
legend('m', 'm_r', 'm_b', 'Location', 'SouthEast');
grid on
ylabel('Machines');

if show_load
    a(end+1)=subplot(313);
    stairs(d(:,1), d(:,3)); ylabel('Clients');
    grid on
    xlabel('Time (s)');
    ylim(ylim+[-100 100])
end

linkaxes(a, 'x');
