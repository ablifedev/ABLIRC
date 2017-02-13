#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE
####################################################################################
#   ：
#   ：
#   ：Joseph Wei
#     ：2015-8-7
#     ：yaxunwei@ablife.cc
####################################################################################
###
####################################################################################
# Date           Version       Author            ChangeLog
#####################################################################################

#####################################################################################
#####
#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "The prog is used to display the cumulatived data of RPKM.

example: Rscript /users/ablife/ablife-R/Bar/Bar_width/v1.0/Bar_width.r
	-f Ezh2_vs_ESC_Input_peaks_length.txt
	-t Ezh2_vs_ESC_Input_peaks_length
	-n Ezh2_vs_ESC_Input_peaks_length
	"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option(c("-t","--title"),action = "store",type = "character",
		help = "The title of the plot"),
	make_option(c("-n", "--filename"),action = "store",type = "character",
		help = "The name of outimage"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
opt <- parse_args(OptionParser(option_list = option_list)) #####

setwd(opt$outdir)						####

###################################################################################
####
###################################################################################
library(ggplot2)
library(reshape2)
library(plotrix)
library(methods)
library(gtable)
library(grid)
###################################################################################


#######data format sample########
#96      1
#110     1
#115     1
#117     1
#118     1
#120     1
#123     2
#126     2
#130     2
#131     1
#133     1
#134     1
#135     3
#137     1
#138     1
#140     1
#141     2
#143     2
#144     2
#145     2
#146     2
#147     4
#
#################################

######Instruction for data#######
#first column is the X axis
#from second to end is the data for ploting
#first row is the head to declare the data
#
#################################


##################################################################################
#
data <- read.table(file= opt$file,header = F)#####	must with header
colname <- colnames(data)
dim_data <- dim(data)
sample <-colname[2]

PeakNum <- sum(data[,2])
SubPeakNum <- 0
for (i in 1:dim_data[1]) {
	SubPeakNum <- SubPeakNum + data[i,2]
	if (SubPeakNum/PeakNum <=0.8) {
		Width <- data[i,1]
	}
}
Label=paste("(Width:",Width,sep="")
Label = paste(Label,",80%)",sep = "")

colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')

title <- gsub('_',' ',opt$title)
ablife_theme_line <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=30,lineheight = 10,colour="#000000",face ="bold",family = "sans"),

		axis.title.x = element_text(size=30,colour = "#000000",face = "bold",family = "sans"),
		axis.title.y = element_text(size=30,colour = "#000000",face = "bold"),
		axis.text.x = element_text(size = 30,colour = "#000000"),
		axis.text.y = element_text(size = 30,,colour = "#000000"),

		legend.title = element_text(size = 15),
		legend.text = element_text(size = 15),
		legend.key.size = unit(1.2,"cm"),
		plot.margin = unit(c(2,2,2,2), "cm"),

		panel.background = element_rect(fill = "white",colour = NA),
		panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		panel.grid.major = element_line(size=0.5,colour = "#FFFFFF"),
		panel.grid.minor = element_line(size=0.1,colour = "#FFFFFF")
		)
}


png(file=paste(opt$filename,'_peak_width.png',sep=''),pointsize=40,width=1000,height=600)
ggplot(data)+ ####
		geom_bar(aes(x = data[,1],y=data[,2],stat = "identity"),colour = "#0000FF",width =1,stat = "identity")+									#####
		labs(title = opt$title,x="Peak Width",y= "Peak Number")+				#####     （  title，    title）
		ablife_theme_line()+
		# scale_y_continuous(limits=c(0,100))+									#####  y
		geom_vline(aes( xintercept = Width),color = "#FF0000") + 							######    ，   X  xintercept
		annotate("text",x=Width,y=max(data[,2])/2,label = Label,size = 8,hjust = 0,colour= "#FF0000")
		# geom_text(aes(x=Width,y=max(data[,2])/2,label=Label),size = 12,hjust = 0,colour = "#FF0000")+
		# scale_colour_hue(name=sample)
#scale_fill_discrete(name="Sample_name")	##           ，label，breaks
