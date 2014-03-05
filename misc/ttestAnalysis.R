data <- read.csv(file="for_alessandro.csv",head=TRUE,sep=",")

t.test(data$sqf,data$brownout,alternative="less",var.equal=TRUE)
t.test(data$sqf,data$brownout,alternative="less")

boxplot(data)
meanStyle <- 19
meanColor <- "black"

rmeans <- c(mean(data$brownout),mean(data$sqf))
points(1:dim(data)[2],rmeans,pch = meanStyle, col = meanColor)