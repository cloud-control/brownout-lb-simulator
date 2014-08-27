results <- read.csv("results-ps-timecut.csv", header=TRUE, comment.char = '#')
results <- results[results$relativeDeviation < 19,]
#results <- results[results$arrivalRate > 10,]

par(mfrow = c(2,2), mar = c(4,4,2,2), oma = c(0,0,1,0))

plot(c(0, max(results$arrivalRate)), c(0, 1.0), type = 'n',
    xlab = 'Arrival Rate [requests / s]', ylab = '')
points(results$arrivalRate, results$optionalRatio, pch = '+', col = 'blue')
points(results$arrivalRate, results$rtMax, pch = '+', col = 'red')
points(results$arrivalRate, results$utilization, pch = '+', col = 'darkgreen')
abline(h = 0.5)
grid()

plot(
  results$relativeDeviation,
  results$rtMax,
  pch = '+',
  xlab = 'Relative deviation of service rate w/ non-essential content',
  ylab = 'rtMax')
abline(h = 0.5)
grid()

# Add legend
par(fig = c(0, 1, 0, 1), oma = c(0, 0, 0, 0), mar = c(0, 0, 0, 0), new = TRUE)
plot(0, 0, type = "n", bty = "n", xaxt = "n", yaxt = "n")
legend('top',
  horiz = TRUE,
  c('optionalRatio', 'rtMax', 'utilization'),
  pch = '+',
  col = c('blue', 'red', 'darkgreen'),
  xpd = TRUE,
  bty = 'n')
