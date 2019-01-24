clc
M = 10000;
x = linspace(0,5,M);
a1 = 0; a2 = 0; a3 = 0;
b1 = 2; b2 = 1; b3 = 4;


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


Umin1 = 1 - (1-U1).*(1-U2);

Umin2 = 1 - (1-U1).*(1-U3);
Umin3 = 1 - (1-U2).*(1-U3);

Umin4 = 1 - (1-U1).*(1-U1);
Umin5= 1 - (1-U2).*(1-U2);
Umin6 = 1 - (1-U3).*(1-U3);

Umin1mean = cumtrapz(x(2:end)'.*diff(Umin1));
Umin1meaner = Umin1mean(end);
Umin2mean = cumtrapz(x(2:end)'.*diff(Umin2));
Umin2meaner = Umin2mean(end);
Umin3mean = cumtrapz(x(2:end)'.*diff(Umin3));
Umin3meaner = Umin3mean(end);
Umin4mean = cumtrapz(x(2:end)'.*diff(Umin4));
Umin4meaner = Umin4mean(end);
Umin5mean = cumtrapz(x(2:end)'.*diff(Umin5));
Umin5meaner = Umin5mean(end);
Umin6mean = cumtrapz(x(2:end)'.*diff(Umin6));
Umin6meaner = Umin6mean(end);

equalityMean = (Umin4meaner + Umin5meaner + Umin6meaner)/3

fastslowMean1 = (2*Umin2meaner + Umin5meaner) / 3
fastslowMean2 = (2*Umin1meaner + Umin6meaner) / 3
fastslowMean3 = (2*Umin3meaner + Umin4meaner) / 3

