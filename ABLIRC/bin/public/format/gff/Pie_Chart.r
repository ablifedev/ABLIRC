#########################################################################################
#                                                                                       #
#   Copyright (c)   A_B_Life 2011                                                       #
#   Writer:         Chrevan Chen <dongchen@ablife.cc>                                   #
#   Program Date:   2011.9.7                                                            #
#   Modifier:       Chrevan Chen <dongchen@ablife.cc>                                   #
#   Last Modified:  2011.9.16                                                           #
#   This script is used for plotting Pie chart                                          #
#                                                                                       #
#########################################################################################

args <- commandArgs(trailingOnly = TRUE)	#get the arguments from the command line
outdir <- args[1]
fileNumber <- args[2]

data <- read.table(file = fileNumber,header=F)
digit <- data[,2]		# The number of each part,we can read them from a file
sum <- sum(digit)			# The sum number of each part
digit <- digit/sum			# The percent
label <- data[,1]	# Label of each part
col <- c('#4682B4','#FF8C00','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#778899','#DAA520','#B22222')
percent <- format(digit*100,digit=2)			# record the first three digit of each percent
percent <- paste(percent,'%',sep='')			# Add the symbol "%"
percent <- paste(label,percent,sep=':')			# Add the symbol "%"
#pdf('Rplot_Pie_Chart.pdf', width = 9, height = 6)
png(file=paste(outdir,'/',fileNumber,'_Pie_Chart.png',sep=''),pointsize=20,width=900,height=600)
par(mar = c(2.1,3.1,3.1,3.1))
#pie(digit,main=fileNumber,labels=percent,edges=400,radius=0.6,col=rainbow(length(digit)),col.lab='blue',font.lab=3,cex.main=2.5,lwd=3)
pie(digit,main=fileNumber,labels=percent,edges=400,radius=0.8,col=col[1:length(digit)],col.lab='blue',font.lab=3,cex.main=2,lwd=3,cex=1.2)
#legend(x='bottomleft',legend=label,col=rainbow(length(digit)),bty='n',text.col=rainbow(length(digit)),pch=15,cex=1)
#dev.off()
#density=1,angle = 45,cex.lab=3,,cex.axis=2,
