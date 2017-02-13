
#!/usr/bin/env Rscript
####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog

# 
#####################################################################################

#####################################################################################

####################################################################################
#####################################################################################

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "The prog is used to display the result of the correlation between two samples choiced by parameters:-s -c

example: Rscript %prog -f /users/ablife/ablife-R/Line/Cor_line/latest/expressed_gene_RPKM.txt.tmp -l 10 -s 2 -c 3 -o ./"

option_list <- list(
	make_option(c("-f", "--file"),action = "store",type = "character",
		help = "The Input RPKM file"),
	make_option(c("-l", "--logValue"),action = "store",type = "character",default = "10",
		help = "The base of the log"),
	make_option(c("-s","--firstsample"),action = "store",type = "integer",
		help = "The first sample to solve the correlation"),
	make_option(c("-c","--secondsample"),action = "store",type = "integer",
		help = "The second sample to solve the correlation"),
	make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
		help = "The outdir")
	)
# parser <- OptionParser(usage = "%prog [option] file",option_list =option)

# arguments <- parse_args(parser,positional_arguments = 2)
opt <- parse_args(OptionParser(option_list = option_list,usage = usage))

if(!is.character(opt$filename)){
	opt$filename = gsub(" ","_",opt$title)
}
log_base <- as.numeric(opt$logValue)
setwd(opt$outdir)

###################################################################################

###################################################################################
library(ggplot2)
library(reshape2)
library(plotrix)
library(methods)
###################################################################################
colour <- c('#85A2EF','#D285EF','#A2EF85','#4682B4','#A0522D','#87CEEB','#6B8E23','#6A5ACD','#E59B95','#EFD285','#B4B643','#2E9AFE','#A1DDBB','#FF8C00')

###################################################################################



data <- read.table(file = opt$file,header = T,sep = '\t',stringsAsFactors=FALSE,check.names = FALSE)
colname <- colnames(data)
colname
x <- log(data[,opt$firstsample]+1,log_base)
y <- log(data[,opt$secondsample]+1,log_base)

Max <- max(max(x),max(y))

CorResult <- cor(x,y,method = 'pearson')
CorResult
CorResult <- round(CorResult,3)
CorResult <- paste("italic(R)==",CorResult,sep='')

# colname[1] <- sub('X.','',colname[1])

#####################################################




######################################################

ablife_theme_Cor <- function(base_size = 12){
	library(grid)		####for using unit function
	theme(
		plot.title = element_text(size=34,lineheight = 10,colour="#000000",face ="bold",family = "sans",vjust = 1),

		axis.title.x = element_text(size=28,colour = "#000000",vjust = 0.5),
		axis.title.y = element_text(size=28,colour = "#000000",vjust = 1),
		axis.text.x = element_text(size = 22,colour = "#000000"),
		axis.text.y = element_text(size = 22,colour = "#000000"),
		axis.ticks.length = unit(0.25,"cm"),
		axis.ticks = element_line(colour = "#000000"), 

		legend.title = element_text(size = 15),
		legend.text = element_text(size = 15),
		legend.key.size = unit(1.2,"cm"),

		panel.background = element_rect(fill = "white",colour = NA),
		# panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
		# panel.grid.major = element_line(size=0.5,colour = "#BFBFBF"),
		# panel.grid.minor = element_line(size=0.1,colour = "#7F7F7F")
		panel.border = element_rect(size = 1.5,colour = "#000000",fill =NA)
		)
}

# outname = gsub(" ","_",Image_name)
png(file=paste(colname[opt$firstsample],'_vs_',colname[opt$secondsample],"_lm.png",sep=''),pointsize=60,width=600,height=600)
ggplot(data)+
		geom_point(aes(x = x,y=y,stat = "identity"),position = "identity",colour = "dodgerblue3")+
		labs(x=colname[opt$firstsample],y= colname[opt$secondsample])+
		ablife_theme_Cor()+
		geom_abline(aes(intercept=0,slope=1),linetype = "dashed",size = 1.5,colour = "gray6")+
		# geom_text(aes(x= 0.4*max(x),y=0.8*max(y),label = CorResult),size =10,fontsize=1,fontface = "italic",parse= TRUE)+
		annotate("text",x= 0.4*max(x),y=0.8*max(y),label = CorResult,size= 12,parse = TRUE)+
		xlim(c(0,Max))



