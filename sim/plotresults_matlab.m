d = dir('results');
dirs = [];
for i = 1:length(d)
    if d(i).isdir == 1
        dirs = [dirs i];
    end
end
d = d(dirs(3:end));

m = length(d);

for i = 1:m
    p = strcat('results/',d(i).name,'/sim-lb.csv');
    load(p)
    
    l = size(sim_lb,2);
    n = (l-3)/5;
    
    t = sim_lb(:,1);
    weights = sim_lb(:,2:n+1);
    dimmers = sim_lb(:,n+2:2*n+1);
    avg_latencies = sim_lb(:,2*n+2:3*n+1);
    max_latencies = sim_lb(:,3*n+2:4*n+1);
    total_requests = [0;diff(sim_lb(:,4*n+2))];
    optional_requests = [0;diff(sim_lb(:,4*n+3))];
    effective_weights = sim_lb(:,4*n+4:5*n+3);
    
    figure(i)
    subplot(321), plot(t,weights), title(d(i).name), ylabel('weights'), grid on
    subplot(322), plot(t,dimmers,t,mean(dimmers,2),'--'), ylabel('dimmer'), grid on
    subplot(323), plot(t,avg_latencies), ylabel('avg latency'), grid on
    subplot(324), plot(t,total_requests,t,optional_requests), ylabel('requests'), legend('Total', 'w. Optional'), grid on
    subplot(325), plot(t,effective_weights), ylabel('eff. weights'), grid on
    disp(sprintf('%s: %d total, %d optional', d(i).name, sum(total_requests), sum(optional_requests)));
    
    if (strcmp(d(i).name,'optimization') && exist('dimmer'))
        figure(100)
        plot(t,dimmers), hold on, plot([t(1) t(end)],[dimmer;dimmer]), hold off
    end
end
