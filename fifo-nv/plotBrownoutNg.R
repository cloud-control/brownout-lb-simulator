qc7 = read.csv('queue-cut-7.csv')
qc8 = read.csv('queue-cut-8.csv')
qc9 = read.csv('queue-cut-9.csv')
tcP = read.csv('time-cut.csv')

par(mar=c(5,4,4,5)+.1, lwd = 2)
plot(c(0, max(tcP$arrivalRate)), c(0.2, 1), type = 'n',
       xlab = "Arrival Rate [requests/s]",
       ylab = "Optional Ratio [%]")
grid()
points(tcP$arrivalRate, tcP$optionalRatio, type = 'l', col = 'darkred'   )
points(qc7$arrivalRate, qc7$optionalRatio, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$optionalRatio, type = 'l', col = 'darkblue'  )
points(qc9$arrivalRate, qc9$optionalRatio, type = 'l', col = 'darkviolet')

par(new=TRUE, lty = 2)
plot(c(0, max(qc9$arrivalRate)), c(0.2, 0.6), type = 'n',
     xaxt = "n", yaxt = "n", xlab = '', ylab = '')
abline(h = 0.5, lty = 1)
points(tcP$arrivalRate, tcP$rtMax, type = 'l', col = 'darkred'   )
points(qc7$arrivalRate, qc7$rtMax, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$rtMax, type = 'l', col = 'darkblue'  )
points(qc9$arrivalRate, qc9$rtMax, type = 'l', col = 'darkviolet')
axis(4)

par(new=TRUE, lty = 4)
points(tcP$arrivalRate, tcP$rtAvg, type = 'l', col = 'darkred'   )
points(qc7$arrivalRate, qc7$rtAvg, type = 'l', col = 'darkgreen' )
points(qc8$arrivalRate, qc8$rtAvg, type = 'l', col = 'darkblue'  )
points(qc9$arrivalRate, qc9$rtAvg, type = 'l', col = 'darkviolet')

par(new=TRUE, lty = 1)
legend('right',
       legend = c('Time Cut (perfect)', 'Queue Cut (q<7)', 'Queue Cut (q<8)', 'Queue Cut (q<9)'),
       col = c('darkred', 'darkgreen', 'darkblue', 'darkviolet'), lty = 1)
