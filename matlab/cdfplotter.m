cdfplot(allOptResponseTimes);
h = gcf;
axesObjs = get(h, 'Children');  %axes handles
dataObjs = get(axesObjs, 'Children'); %handles to low-level graphics objects in axes
objTypes = get(dataObjs, 'Type');  %type of low-level graphics object
xdata = get(dataObjs, 'XData');  %data from low-level grahics objects
ydata = get(dataObjs, 'YData');

fbcdfx = xdata(2:100:end-1);
fbcdfx = [fbcdfx xdata(end)];
fbcdfy = ydata(2:100:end-1);
fbcdfy = [fbcdfy ydata(end)];

close all;
plot(fbcdfx,fbcdfy);

csvVectorcdf = [fbcdfx', fbcdfy'];
csvwrite('distributed-sqf-cdf.csv',csvVectorcdf)


%% plot all

plot(fbcdfx,fbcdfy, 'b');
hold on;
plot(mmcdfx,mmcdfy, 'g');
plot(ffcdfx,ffcdfy, 'r');
plot(ebcdfx,ebcdfy, 'k');


