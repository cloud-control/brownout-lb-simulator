qc7 = read.csv('queue-cut-7.csv')
qc8 = read.csv('queue-cut-8.csv')
tcA = read.csv('time-cut-73.csv')
tcB = read.csv('time-cut-75.csv')

par(mfrow=c(4,1), lwd = 2,
    oma = c(4,1,0,0) + 0.1,
    mar = c(0,4,1,1) + 0.1)

plot(c(0, max(tcA$arrivalRate)), c(0.25, 1), type = 'n',
     xaxt = 'n', ylab = "Optional Ratio [%]")
grid()
points(tcA$arrivalRate, tcA$optionalRatio, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$optionalRatio, type = 'l', col = 'darkviolet')
points(qc7$arrivalRate, qc7$optionalRatio, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$optionalRatio, type = 'l', col = 'darkblue'  )

legend('topright',
       legend = c('Time Cut (timeY=0.073)', 'Time Cut (timeY=0.075)', 'Queue Cut (q<7)', 'Queue Cut (q<8)'),
       col = c('darkred', 'darkviolet', 'darkgreen', 'darkblue'), lty = 1)

plot(c(0, max(tcA$arrivalRate)), c(0.1, 0.6), type = 'n',
     xaxt = 'n', ylab = 'Max RT [s]')
grid()
abline(h = 0.5, lty = 1)
points(tcA$arrivalRate, tcA$rtMax, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$rtMax, type = 'l', col = 'darkviolet')
points(qc7$arrivalRate, qc7$rtMax, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$rtMax, type = 'l', col = 'darkblue'  )

plot(c(0, max(tcA$arrivalRate)), c(0.1, 0.6), type = 'n',
     xaxt = "n", ylab = '99th RT [s]')
grid()
abline(h = 0.5, lty = 1)
points(tcA$arrivalRate, tcA$rt99, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$rt99, type = 'l', col = 'darkviolet')
points(qc7$arrivalRate, qc7$rt99, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$rt99, type = 'l', col = 'darkblue'  )

plot(c(0, max(tcA$arrivalRate)), c(0.92, 0.98), type = 'n',
     xlab = '', ylab = 'Utilization [%]')
grid()
points(tcA$arrivalRate, tcA$utilization, type = 'l', col = 'darkred'   )
points(tcB$arrivalRate, tcB$utilization, type = 'l', col = 'darkviolet')
points(qc7$arrivalRate, qc7$utilization, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$utilization, type = 'l', col = 'darkblue'  )

title(xlab = "Arrival rate [requests/s]",
      outer = TRUE, line = 2)
