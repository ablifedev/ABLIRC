#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog


#####################################################################################


#####################################################################################

#####################################################################################

suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "The prog is used to display Line of data,if you choice '-p 1',then the point is displayed along.

example: Rscript /users/ablife/ablife-R/Line/Line_single/latest/Line_single_ggplot2.r 
	-f inflorescence_minor_ratio_Cumulative_for_acculumulate.txt 
	-t inflorescence_minor_ratio_Cumulative 
	-n inflorescence_minor_ratio_Cumulative  
	-p 1 
"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option(c("-t", "--title"),action = "store",type = "character",
		help = "The title of outimage"),
	make_option(c("-n", "--filename"),action = "store",type = "character",
		help = "The name of outimage"),
	make_option(c("-p","--point"),action = "store",type = "integer",default= 0,
		help = "Point is displayed"),
	make_option("--xmin",action = "store",type = "character",
		help = "Restrict the min x"),
	make_option("--xmax",action = "store",type = "character",
		help = "Restrict the max x"),
	make_option("--ymin",action = "store",type = "character",
		help = "Restrict the min y"),
	make_option("--ymax",action = "store",type = "character",
		help = "Restrict the max y"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
opt <- parse_args(OptionParser(option_list = option_list,usage = usage))

setwd(opt$outdir)						####

###################################################################################

###################################################################################
library(ggplot2)
library(reshape2)
library(plotrix)
library(methods)
library(gtable)
library(grid)
###################################################################################
colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')


#######data format sample########
# key     accumulative_value
# 0.01    139
# 0.02    237
# 0.03    302
# 0.04    382
# 0.05    438
# 0.06    501
# 0.07    549
# 0.08    610
# 0.09    655
# 0.10    709
# #
#################################

######Instruction for data#######
#first column is the X axis
#from second to end is the data for ploting
#first row is the head to declare the data
#
#################################

###################################################################################

data <- read.table(file = opt$file,header = T)
colname <- colnames(data)
colname[1] <- sub('X.','',colname[1])

title <- gsub('_',' ',opt$title)
sample <- colname[2]
Max_x <- max(data[,1])
Max_y <- max(data[,2])
Min_x <- min(data[,1])
Min_y <- min(data[,2])

ablife_theme_line <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=12,lineheight = 10,colour="#000000",vjust = 1),

		axis.title.x = element_text(size=12,colour = "#000000"),
		axis.title.y = element_text(size=12,colour = "#000000",vjust = 1),
		axis.text.x = element_text(size = 12,colour = "#000000"),
		axis.text.y = element_text(size = 12 ,colour = "#000000"),
		axis.ticks = element_line(colour = "#000000"),
		axis.ticks.length = unit(0.25,"cm"),

		legend.title = element_text(size = 12),
		legend.text = element_text(size = 12),
		legend.key.size = unit(1.2,"cm"),

		panel.background = element_rect(colour="black")
		# panel.background = element_rect(fill = "white",colour = NA),
		# panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		# panel.grid.major = element_line(size=0.5,colour = "#BFBFBF"),
		# panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		)
}


# png(file=paste(opt$filename,'_Line.png',sep=''),pointsize=40,width=1000,height=600)
Line <- ggplot(data)+
		geom_line(aes(x = data[,1],y=data[,2],stat = "identity",group = 1),colour = colour[12],size =1,position = "identity")+
		labs(title = title,x=colname[1],y= colname[2])+
		ablife_theme_line()+

		scale_colour_hue(name=sample)
if(is.character(opt$xmin)){
	X_min <- as.numeric(opt$xmin)
}else{
	X_min <- Min_x
}

if(is.character(opt$xmax)){
	X_max <- as.numeric(opt$xmax)
}else{
	X_max <- Max_x
}

if(is.character(opt$ymin)){
	Y_min <- as.numeric(opt$ymin)
}else{
	Y_min <- Min_y
}

if(is.character(opt$ymax)){
	Y_max <- as.numeric(opt$ymax)
}else{
	Y_max <- Max_y
}
Line <- Line + scale_x_continuous(limits=c(X_min,X_max))+scale_y_continuous(limits=c(Y_min,Y_max))

if(opt$point ==1){
	Line + geom_point(aes(x = data[,1],y=data[,2],stat = "identity"),colour = colour[12],size = 2,shape = 19)
}else{
	Line
}

ggsave(file = paste(opt$filename,"_Line.pdf",sep=''), width = 180,height = 120,dpi = 450,units = "mm")
ggsave(file = paste(opt$filename,"_Line.png",sep=''), width = 180,height = 120,dpi = 450,units = "mm")