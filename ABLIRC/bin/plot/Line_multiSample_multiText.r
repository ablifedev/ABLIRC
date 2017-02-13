#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog


# 2016-8-16		v3.0		  Weiyaxun
#####################################################################################

#####################################################################################


####################################################################################

#####################################################################################

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "The prog is used to display the distribution of TSS,TTS,startcondon,stopcodon,and there is a break between TTS and TSS.	But this prog can be used to display any multi lines.

example: Rscript /users/ablife/ablife-R/Line/Line_multi/latest/Line_multiSample_multiText.r 
	-f /users/ablife/ablife-R/Line/Line_multi/latest/inflorescence_distance2startcodon_reads_density.txt,/users/ablife/ablife-R/Line/Line_multi/latest/inflorescence_distance2stopcodon_reads_density.txt 
	-s startcondon,stopcodon 
	-t inflorescence_distance2xxx_reads_density_codon"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input file"),
	make_option(c("-s", "--samplename"),action = "store",type = "character",
		help = "The Input sample name"),
	make_option(c("-t", "--title"),action = "store",type = "character",
		help = "The title of outimage"),
	make_option(c("-n", "--filename"),action = "store",type = "character",
		help = "The name of outimage"),
	make_option(c("-l","--length"),action = "store",type = "integer",default = "2",
		help = "The length bewteen start to end"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
# parser <- OptionParser(usage = "%prog [option] file",option_list =option)

# arguments <- parse_args(parser,positional_arguments = 2)
opt <- parse_args(OptionParser(option_list = option_list,usage=usage))

if(!is.character(opt$filename)){
	opt$filename = gsub(" ","_",opt$title)
}

setwd(opt$outdir)

###################################################################################

###################################################################################
library(ggplot2)
library(reshape2)
library(plotrix)
library(methods)
library(RColorBrewer)
###################################################################################
# colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')
colour1 <- brewer.pal(8,"Dark2")
colour2 <- brewer.pal(9,"Set1")
colour3 <- brewer.pal(12,"Paired")
colour<- c(colour1,colour2,colour3)
# colour <-c(colour3[2:12],colour2[8],colour1[4],colour1[7],colour1[8])
# colour <-c("#3C5488CC","#E64B35FF","#4DBBD5FF","#00A087FF",colour1[2],colour1[6:8])

###################################################################################


file <- strsplit(opt$file,",")[[1]]
samplename <- strsplit(opt$samplename,",")[[1]]
data <- c()

for(i in 1:length(file)){
	samplename[i] <- gsub('_distance2startcodon','',samplename[i])
	samplename[i] <- gsub('_distance2stopcodon','',samplename[i])
	samplename[i] <- gsub('_distance2tts','',samplename[i])
	samplename[i] <- gsub('_distance2tss','',samplename[i])
	text <- read.table(file = file[i],header = TRUE)
	if(grepl("stopcodon",file[i]) || grepl("tts",file[i])){
	# if(grepl("stopcodon",samplename[i]) || grepl("tts",samplename[i])){
	# if(samplename[i] == "stopcodon" || samplename[i] == "tts"){
		text[,1] <- text[,1]+opt$length*max(text[,1])+500
	}
	text[,3] <- samplename[i]
	text[,4] <- colour[i]
	data <- rbind(data,text)
}
Max <- max(data[,2])
samplename
colname <- colnames(text)		

colname[1] <- sub('X.','',colname[1])
title <- gsub('_',' ',opt$title)
#####################################################




######################################################

ablife_theme_line <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=12,lineheight = 10,colour="#000000",vjust = 1),

		axis.title.x = element_text(size=12,colour = "#000000",vjust = 0.5),
		axis.title.y = element_text(size=12,colour = "#000000",vjust = 1),
		axis.text.x = element_text(size = 12,colour = "#000000"),
		axis.text.y = element_text(size = 12 ,colour = "#000000"),
		axis.ticks.length = unit(0.1,"cm"),
		axis.ticks = element_line(colour = "#000000"), 

		# legend.title = element_text(size = 9),
		legend.title = element_blank(),
		legend.text = element_text(size = 9),
		legend.key.size = unit(0.5,"cm"),

		panel.background = element_rect(colour = "black")
		# panel.background = element_rect(fill = "white",colour = NA),
		# # panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		# # panel.grid.major = element_line(size=0.1,colour = "#BFBFBF"),
		# # panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		# panel.border = element_rect(size = 1,colour = "#000000",fill =NA),
		# panel.grid.major.x = element_line(size=0.3,colour = "#000000"),
		# panel.grid.major.y = element_line(size=0.1,colour = "#909090",linetype = "dotted"),
		# panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		)
}

# outname = gsub(" ","_",Image_name)
# png(file=paste(opt$filename,".png",sep=''),pointsize=40,width=1000,height=600)
ggplot(data)+
		geom_line(aes(x = data[,1],y=data[,2],stat = "identity",group = data[,4],colour = data[,3]),size =1,position = "identity")+
		labs(title = title,x=colname[1],y= colname[2])+
		ablife_theme_line()+
		theme(
			# legend.position = c(0.8, 0.78), #adjust for needing
			# legend.position = "right",
			legend.background = element_blank(),
			legend.key = element_blank()
			# legend.direction = "horizontal"
			)+
		scale_x_continuous(breaks = c(-1000,0,1000,1500,2500,3500),labels = c(-1000,"0\n(5')",1000,-1000,"0\n(3')",1000))+
		scale_y_continuous(limits=c(min(data[,2]),Max+10))+

		scale_colour_manual("Type",values = colour[1:length(samplename)])
ggsave(file = paste(opt$filename,".pdf",sep=''), width = 310,height = 150,dpi = 450,units = "mm")
ggsave(file = paste(opt$filename,".png",sep=''), width = 310,height = 150,dpi = 450,units = "mm")
