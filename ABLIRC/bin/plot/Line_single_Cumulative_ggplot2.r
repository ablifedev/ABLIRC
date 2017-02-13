#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog



#####################################################################################

#######################################################################################
#
#This can be used to plot 2 y axis and to show the data with unit
#
#######################################################################################

#####################################################################################

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "The prog is used to display the cumulatived data of RPKM.

example: Rscript /users/ablife/ablife-R/Line/Line_cumu/latest/Line_single_Cumulative_ggplot2.r 
	-f /users/ablife/ablife-R/Line/Line_cumu/latest/inflorescence_RPKM_Cumulative.txt
	-t inflorescence_RPKM
	-n inflorescence_RPKM
	"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option("--log",action = "store_true",default = FALSE,
		help = "handel the data using log"),
	make_option(c("-t", "--title"),action = "store",type = "character",
		help = "The title of outimage"),
	make_option(c("-n", "--filename"),action = "store",type = "character",
		help = "The name of outimage"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
opt <- parse_args(OptionParser(option_list = option_list))

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
#key     accumulative_value
# 0.01    139
# 0.02    237
# 0.03    302
# 0.04    382
# 0.05    438
# 0.06    501
# 0.07    549
# 0.08    610
# 0.09    654
# 0.10    709
# 0.11    759
# 0.12    799
# 0.13    848
# 0.14    888
# 0.15    929
# 
#
#################################

######Instruction for data#######
#first column is the X axis
#from second to end is the data for ploting
#first row is the head to declare the data
#
#################################


###################################################################################

data <- read.table(file= opt$file,header = T,sep = "\t")#####	must with header
colname <- colnames(data)
colname[1] <- sub('X.','',colname[1])
dim_data <- dim(data)
sample <-colname[3]
percent_10 <- abs(data[,2]-10)
percent_50 <- abs(data[,2]-50)
num_10 <- min(which(percent_10 == min(percent_10),arr.ind = TRUE))
num_50 <- min(which(percent_50 == min(percent_50),arr.ind = TRUE))
label_10 <- paste("(",data[num_10,1],sep='')
label_10 <- paste(label_10,data[num_10,2],sep = '，')
label_10 <- paste(label_10,"%)",sep = '')

label_50 <- paste("(",data[num_50,1],sep = '')
label_50 <- paste(label_50,data[num_50,2],sep = '，')
label_50 <- paste(label_50,"%)",sep = '')

First_Y = seq(0,1,by=0.2)*data[dim_data[1],3]
First_label = round(First_Y,0)
Sencond_Y=seq(0,100,by=20)
percent = paste(Sencond_Y,'%')

title <- gsub('_',' ',opt$title)
ablife_theme_line <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=34,lineheight = 10,colour="#000000",face ="bold",family = "sans",vjust = 0.5),

		axis.title.x = element_text(size=28,colour = "#000000",face = "bold",family = "sans",vjust = -0.1
			),
		axis.title.y = element_text(size=28,colour = "#000000",face = "bold",vjust = 1),
		axis.text.x = element_text(size = 22,colour = "#000000"),
		axis.text.y = element_text(size = 22 ,colour = "#000000"),
   		axis.ticks.length = unit(0.25,"cm"),
		axis.ticks = element_line(colour = "#000000"), 

		legend.title = element_text(size = 15),
		legend.text = element_text(size = 15),
		legend.key.size = unit(1.2,"cm"),

		panel.background = element_rect(fill = "white",colour = NA),
		# panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		# panel.grid.major = element_line(size=0.5,colour = "#BFBFBF"),
		# panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		panel.border = element_rect(size = 1.5,colour = "#000000",fill =NA),
		panel.grid.major.x = element_line(size=0.5,colour = "#909090"),
		panel.grid.major.y = element_line(size=0.5,colour = "#909090",linetype = "dotted"),
		panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		)
}

png(file=paste(opt$filename,'_Cumulative_Line.png',sep=''),pointsize=40,width=1000,height=600)
grid.newpage()
p1 <- ggplot(data)+
		geom_line(aes(x = data[,1],y=data[,3],stat = "identity",group = 1),colour = colour[12],size =1.5,position = "identity")+
		labs(title = title,x=colname[1],y= colname[3])+
		ablife_theme_line()+
		scale_y_continuous(labels = First_label,breaks = First_Y)+
		scale_colour_hue(name=sample)+

		scale_x_continuous(limits=(c(0,100)))
#
p2 <- ggplot(data)+
		geom_line(aes(x = data[,1],y=data[,2],stat = "identity",group = 1),colour = colour[12],size =1.5,position = "identity")+
		labs(title = title,x=colname[1],y= colname[2])+
		ablife_theme_line()+
		scale_y_continuous(labels = percent,breaks=Sencond_Y)+
		scale_colour_hue(name=sample)+

		# # geom_segment(aes(x=c(data[num_10,1],data[num_50,1]),y=c(0,0),xend=c(data[num_10,1],data[num_50,1]),yend = c(yend1,yend2)),colour = '#339900',size = 0.5)+
		# geom_segment(aes(x=data[num_10,1],y=0,xend = data[num_10,1],yend = data[num_10,2]),colour = "#339900",size=0.5)+
		# geom_segment(aes(x=data[num_50,1],y=0,xend = data[num_50,1],yend = data[num_50,2]),colour = "#339900",size=0.5)+
		geom_hline(aes(yintercept = data[num_10,2]),colour = "#909090",size = 0.7)+
		geom_hline(aes(yintercept = data[num_50,2]),colour = "#909090",size = 0.7)+
		geom_point(aes(x=data[num_10,1],y=data[num_10,2]),shape=21,size = 5,colour = "#666666")+
		geom_point(aes(x=data[num_50,1],y=data[num_50,2]),shape=21,size = 5,colour = "#666666")+
		annotate("text",x= c(data[num_10,1],data[num_50,1]),y=c(data[num_10,2],data[num_50,2]),label = c(label_10,label_50),hjust = -0.3,vjust = -1,size=8)+
		scale_x_continuous(limits=(c(0,100)))
g1 <- ggplot_gtable(ggplot_build(p1))
g2 <- ggplot_gtable(ggplot_build(p2))

pp <- c(subset(g1$layout,name == "panel",se = t:r))
g<-gtable_add_grob(g1,g2$grobs[[which(g2$layout$name == "panel")]],pp$t,pp$l,pp$b,pp$l)

ia <- which(g2$layout$name == "axis-l")
ga <- g2$grobs[[ia]]
ax <- ga$children[[2]]
ax$widths <- rev(ax$widths)
ax$grobs <- rev(ax$grobs)
ax$grobs[[1]]$x <- ax$grobs[[1]]$x - unit(1,"npc") + unit(0.15,"cm")
g <- gtable_add_cols(g,g2$widths[g2$layout[ia, ]$l],length(g$widths) -1)
g <- gtable_add_grob(g,ax,pp$t,length(g$widths)-1,pp$b)

grid.draw(g)
