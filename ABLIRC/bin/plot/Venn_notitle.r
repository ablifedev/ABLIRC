#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog

# 2015-8-13		 v2.0          Weiyaxun
#####################################################################################

#####################################################################################

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option(c("-d","--dataname"),action = "store",type = "character",
		help = "The dataname ; default is the file"),
	make_option(c("-c","--column"),action = "store",type = "integer",default = 1,
		help = "The column that we want;default = 1"),
	make_option(c("-t", "--title"),action = "store",type = "character",default = "Venn Diagram",
		help = "The title of outimage;default = Ven Diagram"),
	make_option(c("-n", "--filename"),action = "store",type = "character",default = "Venn",
		help = "The name of outimage;default = Venn"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
opt <- parse_args(OptionParser(option_list = option_list))
setwd(opt$outdir)


###################################################################################

###################################################################################
library(VennDiagram)
library(gplots)
##################################################################################

###################################################################################

file <- strsplit(opt$file,",")[[1]]
dataname <- c()

len <- length(file)
if(!is.character(opt$dataname)){
	for(i in 1:len){
		dataname_temp <- strsplit(as.character(file[i]),"/")
		dataname[i] <- sub("_DEG.txt","",dataname_temp[[1]][length(dataname_temp[[1]])])
		dataname[i] <- sub("^_","",dataname[i])
	}
}else{
	dataname <- strsplit(opt$dataname,",")[[1]]
}
group <- vector(mode='list',length=len)

for (i in 1:(len)) {
	data <- read.table(file=file[i],header=F,sep="\t",quote = "")
	group[[i]] <- data[,opt$column]
	# if(!is.character(opt$dataname)){
	# 	dataname_temp = strsplit(file[i],".")
	# 	names(group)[i] <- dataname_temp[1]
	# }else{
	# 	names(group)[i] <- dataname[i]
	# }
	names(group)[i] <- dataname[i]
}
# names(group)
if (len == 4){
	venn.diagram(
	group,
	filename = paste(opt$filename,"png",sep="."),
	col = "black",
	lty = "dotted",
	lwd = 4,
	fill = c("cornflowerblue", "green", "yellow", "darkorchid1"),
	alpha = 0.50,
	label.col = c("orange", "white", "darkorchid4", "white", "white", "white", "white", "white", "darkblue", "white", "white", "white", "white", "darkgreen", "white"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("darkblue", "darkgreen", "orange", "darkorchid4"),
	cat.cex = 0.8,
	cat.fontfamily = "serif",
	imagetype = "png",
	main = opt$title,
	main.cex = 2
	#margin = 0.1
	);
	}else if(len == 1){
	venn.diagram(
	group,
	filename = paste(opt$filename,"png",sep="."),
	col = "black",
	lwd = 9,
	fontface = "bold",
	fill = "grey",
	alpha = 0.75,
	cex = 4,
	cat.cex = 1,
	cat.fontface = "bold",
	imagetype = "png",
	main = opt$title
	);
	}else if (len == 2){
	venn.diagram(
	group,
	filename = paste(opt$filename,"png",sep="."),
	lwd = 4,
	fill = c("cornflowerblue", "darkorchid1"),
	alpha = 0.75,
	label.col = "black",	###the colour for each area label
	cex = 2,		###the size for each area label 
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("cornflowerblue", "darkorchid1"),
	cat.cex = 1,	##size of category name  
	cat.fontfamily = "serif",
	cat.fontface = "bold",	##fontface of category name 
	cat.dist = c(0.03, 0.03),	###distance from the edge of the circle of category name(can be negative)
	cat.pos = c(0, 30),
	imagetype = "png",
	main = opt$title,
	margin = 0.01 		###the amount of whitespace around the diagram in grid units  
	);
	}else if(len == 3){
	venn.diagram(
	group,
	filename = paste(opt$filename,"png",sep="."),
	lwd = 4,
	col = "transparent",
	fill = c("red", "blue", "green"),
	alpha = 0.5,
	label.col = c("darkred", "white", "darkblue", "white", "white", "white", "darkgreen"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.default.pos = "text",
	cat.col = c("darkred", "darkblue", "darkgreen"),
	cat.cex = 1,
	cat.fontfamily = "serif",
	cat.dist = c(0.06, 0.06, 0.03),
	cat.pos = 0,
	imagetype = "png",
	main = opt$title
	);
	}
