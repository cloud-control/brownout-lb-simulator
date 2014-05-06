fast = 1;   % if fast = 1, the aggregated measurements from sim_lb are used, otherwise use actual server measurements

resdir = '../results/';
d = dir(resdir);
dirs = [];
for i = 1:length(d)
    if d(i).isdir == 1
        dirs = [dirs i];
    end
end
d = d(dirs(3:end));

m = length(d);

r_names = {};
r_total = [];
r_opt = [];
for i = 1:m
    p = strcat(resdir,d(i).name,'/sim-lb.csv');
    load(p)
    
    l = size(sim_lb, 2);
    n = (l-3)/5;
    
    t_lb = sim_lb(:,1);
    weights = sim_lb(:,2:n+1);
    total_requests = [0;diff(sim_lb(:,4*n+2))];
    optional_requests = [0;diff(sim_lb(:,4*n+3))];
    effective_weights = sim_lb(:,4*n+4:5*n+3);
    
    if fast == 1
        t = t_lb;
        dimmers = sim_lb(:,n+2:2*n+1);
        avg_latencies = sim_lb(:,2*n+2:3*n+1);
        max_latencies = sim_lb(:,3*n+2:4*n+1);
    else
        load(strcat(resdir,d(i).name,'/sim-server1.csv'));
        t = sim_server1(:,1);
        dimmers = zeros(length(sim_server1),n);
        avg_latencies = zeros(length(sim_server1),n);
        max_latencies = zeros(length(sim_server1),n);
        
        for j = 1:n
            pp = strcat(resdir,d(i).name,'/sim-server',num2str(j),'.csv');
            curr_server = load(pp);
            dimmers(:,j) = curr_server(:,4);
            avg_latencies(:,j) = curr_server(:,2);
            max_latencies(:,j) = curr_server(:,3);
        end
    end

   
    
    figure(i)
    a=[];
    a(end+1)=subplot(321); plot(t_lb,weights), title(d(i).name), ylabel('weights'), grid on
    a(end+1)=subplot(322); plot(t,dimmers,t,mean(dimmers,2),'--'), ylabel('dimmer'), grid on
    a(end+1)=subplot(323); plot(t,avg_latencies), ylabel('avg latency'), grid on
    a(end+1)=subplot(324); plot(t_lb,total_requests,t_lb,optional_requests), ylabel('requests'), legend('Total', 'w. Optional'), grid on
    a(end+1)=subplot(325); plot(t_lb,effective_weights), ylabel('eff. weights'), grid on
    a(end+1)=subplot(326); plot(t, dimmers(:,1)-mean(dimmers,2)), grid on
    linkaxes(a, 'x');
    r_names{end+1} = d(i).name;
    r_total(end+1) = sim_lb(end,4*n+2);
    r_opt(end+1) = sim_lb(end,4*n+3);
    
    %if (strcmp(d(i).name,'optimization') && exist('dimmer'))
    %    figure(100)
    %    plot(t,dimmers), hold on, plot([t(1) t(end)],[dimmer;dimmer]), hold off
    %end
end

[ans, si] = sort(-r_opt./max(r_total));
for i=si
    disp(sprintf('%s: %d total, %d optional, %.2f%% of max total', r_names{i}, r_total(i), r_opt(i), r_opt(i)*100/max(r_total)));
end

