if (!exists("discipline")) {
  stop("Please set the discipline variable")
}
results <- read.csv(paste("results-", discipline, ".csv", sep = ''), header=TRUE, comment.char = '#')

par(mfrow = c(2, 1), mar = c(4,4,2,2))
plot(c(0, max(results$arrivalRate)), c(0, 1.0), type = 'n',
    xlab = 'Arrival Rate [requests / s]', ylab = '')
points(results$arrivalRate, results$optionalRatio, pch = '+', col = 'blue')
points(results$arrivalRate, results$rtMax, pch = '+', col = 'red')
points(results$arrivalRate, results$utilization, pch = '+', col = 'darkgreen')
abline(h = 0.5)
grid()

par(xpd=TRUE)
legend(10, 1.31,
      horiz = TRUE,
      c('optionalRatio', 'rtMax', 'utilization'),
      pch = '+',
      col = c('blue', 'red', 'darkgreen'))
par(xpd=FALSE)

plot(
  results$timeYsigma[results$arrivalRate > 10],
  results$rtMax[results$arrivalRate > 10],
  pch = '+',
  xlab = 'sigma',
  ylab = 'rtMax')
abline(h = 0.5)
grid()