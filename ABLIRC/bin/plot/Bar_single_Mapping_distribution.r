#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog



# 2016-8-16		 v2.0
#####################################################################################

#####################################################################################

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "Rscript /users/ablife/ablife-R/Bar/Bar_Rpkm/latest/Bar_single_Mapping_distribution.r -f -t -n -o

example: Rscript /users/ablife/ablife-R/Bar/Bar_Rpkm/latest/Bar_single_Mapping_distribution.r 
		-f /users/ablife/ablife-R/Bar/Bar_Rpkm/latest/Mapping_distribution.txt
		-t Mapping_distribution
		-n Mapping_distribution
		-o ./"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option(c("-t", "--title"),action = "store",type = "character",
		help = "The title of outimage"),
	make_option(c("-n", "--filename"),action = "store",type = "character",
		help = "The name of outimage"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
opt <- parse_args(OptionParser(option_list = option_list,usage=usage))

setwd(opt$outdir)						####

###################################################################################

###################################################################################
library(ggplot2)
library(reshape2)
library(plotrix)
library(methods)
###################################################################################
colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')

#######data format sample########
#type	sample1
#CDS	4940.93
#noncoding_exon	14008.73
#five_prime_UTR	7765.00
#intergenic	4687472.87
#intron	1719.35
#three_prime_UTR	273.12
#
#################################

######Instruction for data#######
#first column is the X axis
#from second to end is the data for ploting
#first row is the head to declare the data
#
#################################


###################################################################################

title <- gsub('_',' ',opt$title)
data <- read.table(file= opt$file,header = T,sep = "\t")#####	must with header
colname <- colnames(data)
dim_data <- dim(data)
sample <-colname[2]
data<-data[order(data[,2]),]

newdata <- data
percent <-data[,2]
label <- data[,1]

percent <- percent/sum(percent)
percent <- round(percent*100,2)
newdata[,2] <- percent

Percent <- paste(percent,'%',sep='')	###for show
percentage <- paste(percent,'%)',sep='')
label <- paste(label,percentage,sep='(')
colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')

ablife_theme_bar <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=12,lineheight = 10,colour="#000000",vjust=1),

		axis.title.x = element_text(size=12,colour = "#000000"),
		axis.title.y = element_text(size=12,colour = "#000000"),
		axis.text.x = element_text(size = 12,colour = "#000000"),
		axis.text.y = element_text(size = 12 ,colour = "#000000"),
		axis.ticks.length = unit(0.2,"cm"),
		axis.ticks = element_line(colour = "#000000"), 

		legend.title = element_text(size = 12),
		legend.text = element_text(size = 12),
		legend.key.size = unit(1.2,"cm"),

		panel.background = element_rect(colour="black")
		# panel.background = element_rect(fill = "white",colour = NA),
		# # panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		# panel.border = element_rect(size = 1.5,colour = "#000000",fill =NA),
		# # panel.grid.major = element_line(size=0.5,colour = "#BFBFBF"),
		# panel.grid.major.x = element_line(size=0.5,colour = "#909090"),
		# panel.grid.major.y = element_line(size=0.5,colour = "#909090",linetype = "dotted"),
		# panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		)
}


# png(file=paste(opt$filename,'_Bar.png',sep=''),pointsize=40,width=1000,height=600)
ggplot(newdata)+
		geom_bar(aes(x = c(1:dim_data[1]) ,y=newdata[,2],fill = label,stat = "identity"),width = 0.5,stat = "identity")+

		labs(x="Genomic Region",y= "Percentage(%)")+
		coord_flip()+
		geom_text(aes(x=c(1:dim_data[1]) ,y=newdata[,2],label=Percent),size = 4,hjust = -0.1)+
		theme(legend.position = 'none')+
		ablife_theme_bar()+
		scale_y_continuous(limits=c(0,100))+
		scale_x_reverse(breaks= c(1:dim_data[1]) ,labels=newdata[,1])+
		scale_fill_manual(name=sample,values = colour[1:dim_data[1]])

ggsave(file = paste(opt$filename,"_Bar.pdf",sep=''), width = 180,height = 120,dpi = 450,units = "mm")
ggsave(file = paste(opt$filename,"_Bar.png",sep=''), width = 180,height = 120,dpi = 450,units = "mm")
