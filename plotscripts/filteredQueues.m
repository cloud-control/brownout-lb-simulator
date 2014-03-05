clc;

t=A(:,1); Q=A(:,2:6);

t = t-t(1);
idx=find(t>=min(1000,t(end)),1);
tf = t(1:idx);

p = 0.95;
Qf = zeros(1,size(Q,2));
for kk=2:idx,
    Qf(kk,:) = p*Qf(kk-1,:) + (1-p)*Q(kk-1,:);
end


%% Plotting queues
figure(1); clf;
subplot(211);
 plot(t,Q);
 xlabel('time (s)');
 title('Actual queues');
subplot(212);
 plot(tf,Qf);
 xlabel('time (s)');
 title('Filtered queues queues');