results <- read.csv("~/work/2013-brownout/brownout-lb-simulator/results-ps.csv", header=TRUE, comment.char = '#')

par(mfrow = c(2, 1), mar = c(4,4,2,2))
plot(c(0, max(results$arrivalRate)), c(0, 1), type = 'n',
    xlab = 'Arrival Rate [requests / s]', ylab = '')
points(results$arrivalRate, results$optionalRatio, pch = '+', col = 'blue')
points(results$arrivalRate, results$rtMax, pch = '+', col = 'red')
abline(h = 0.5)
grid()

legend('topright',
      c('optionalRatio', 'rtMax'),
      pch = '+',
      col = c('blue', 'red'))

plot(
  results$timeYsigma[results$arrivalRate > 10],
  results$rtMax[results$arrivalRate > 10],
  pch = '+',
  xlab = 'sigma',
  ylab = 'rtMax')
abline(h = 0.5)
grid()