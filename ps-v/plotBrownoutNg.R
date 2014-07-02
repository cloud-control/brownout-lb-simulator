qcA = read.csv('queue-cut-6.csv')
qcB = read.csv('queue-cut-est.csv')
tcA = read.csv('queue-cut-est-hv.csv')
tcB = read.csv('time-cut-est.csv')

par(mfrow=c(4,1), lwd = 2,
    oma = c(4,1,0,0) + 0.1,
    mar = c(0,4,1,1) + 0.1)

plot(c(0, max(tcA$arrivalRate)), c(0.25, 1), type = 'n',
     xaxt = 'n', ylab = "Optional Ratio [%]")
grid()
points(tcA$arrivalRate, tcA$optionalRatio, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$optionalRatio, type = 'l', col = 'darkviolet')
points(qcA$arrivalRate, qcA$optionalRatio, type = 'l', col = 'darkgreen' )
points(qcB$arrivalRate, qcB$optionalRatio, type = 'l', col = 'darkblue'  )

legend('topright',
       legend = c('Queue Cut HV', 'Time Cut (est)', 'Queue Cut (q<6)', 'Queue Cut (est)'),
       col = c('darkred', 'darkviolet', 'darkgreen', 'darkblue'), lty = 1)

plot(c(0, max(tcA$arrivalRate)), c(0.1, 0.6), type = 'n',
     xaxt = 'n', ylab = 'Max RT [s]')
grid()
abline(h = 0.5, lty = 1)
points(tcA$arrivalRate, tcA$rtMax, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$rtMax, type = 'l', col = 'darkviolet')
points(qcA$arrivalRate, qcA$rtMax, type = 'l', col = 'darkgreen' )
points(qcB$arrivalRate, qcB$rtMax, type = 'l', col = 'darkblue'  )

plot(c(0, max(tcA$arrivalRate)), c(0.1, 0.6), type = 'n',
     xaxt = "n", ylab = '99th RT [s]')
grid()
abline(h = 0.5, lty = 1)
points(tcA$arrivalRate, tcA$rt99, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$rt99, type = 'l', col = 'darkviolet')
points(qcA$arrivalRate, qcA$rt99, type = 'l', col = 'darkgreen' )
points(qcB$arrivalRate, qcB$rt99, type = 'l', col = 'darkblue'  )

plot(c(0, max(tcA$arrivalRate)), c(0.97, 1.0), type = 'n',
     xlab = '', ylab = 'Utilization [%]')
grid()
points(tcA$arrivalRate, tcA$utilization, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$utilization, type = 'l', col = 'darkviolet')
points(qcA$arrivalRate, qcA$utilization, type = 'l', col = 'darkgreen' )
points(qcB$arrivalRate, qcB$utilization, type = 'l', col = 'darkblue'  )

title(xlab = "Arrival rate [requests/s]",
      outer = TRUE, line = 2)
