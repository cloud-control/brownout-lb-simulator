M = 10000;
x = linspace(0,5,M);
a1 = 0; a2 = 1; a3 = 0.5;
b1 = 2; b2 = 1.5; b3 = 4;


U1 = zeros(M,1);
U2 = zeros(M,1);
U3 = zeros(M,1);

j = 1;
for i=x
    if (a1<=x(j)) && (x(j)<=b1)
        U1(j) = (x(j)-a1)/(b1-a1);
    elseif x(j)>b1
        U1(j) = 1;
    end
    
    if (a2<=x(j)) && (x(j)<=b2)
        U2(j) = (x(j)-a2)/(b2-a2);
    elseif x(j)>b2
        U2(j) = 1;
    end
    
    if (a3<=x(j)) && (x(j)<=b3)
        U3(j) = (x(j)-a3)/(b3-a3);
    elseif x(j)>b3
        U3(j) = 1;
    end     
    
        
  j = j + 1;
end

Umin = 1 - (1-U1).*(1-U2).*(1-U3);

Uminmean = cumtrapz(x(2:end)'.*diff(Umin));

csvwrite('x.csv', x');
csvwrite('umin.csv', Umin);


plot(x, U1, 'r');
hold on;
plot(x, U2, 'b');
plot(x, U3, 'g');
plot(x, Umin, 'k');