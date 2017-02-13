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

#####################################################################################
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

usage = "Rscript /users/ablife/ablife-R/Venn/latest/Venn.r -f -d -c -t -n

example: Rscript /users/ablife/ablife-R/Venn/latest/Venn.r
-f Ezh2_vs_ESC_Input_peaks_cluster.bed,Jarid2_vs_ESC_Input_peaks_cluster.bed
-c 6
-o ./"

option_list <- list(
  make_option(c("-f", "--file"),action = "store",type = "character",
              help = "The Result file"),
  make_option(c("-A","--columnA"),action = "store",type = "integer",default = 5,
              help = "the column number of sample A's Expression"),
  make_option(c("-B","--columnB"),action = "store",type = "integer",default = 6,
              help = "the column number of sample B's Expression"),
  make_option(c("-s", "--suffix"),action = "store",type = "character",default = "_result_list_add_exp.txt",
              help = "file suffix,which will be delete in result file name"),
  make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
              help = "The outdir"),
  make_option(c("-n", "--outfile"),action = "store",type = "character",default = "NULL",
              help = "outfile name"),
  make_option(c("-c", "--addcor"),action = "store",type = "integer",default = 1,
              help = "add R value, default is 1, set 0 to disable")
)
opt <- parse_args(OptionParser(option_list = option_list))
setwd(opt$outdir)

# opt$file <- "S_24h_vs_C_24h_result_list.txt"

a <- as.numeric(opt$columnA)
b <- as.numeric(opt$columnB)
#################2016.05.27
#setwd("")
#################
library(grid)# for `unit`
library(gridExtra)# for `unit
library(ggplot2)
library(reshape2)
library(dplyr)

################################################################################

################################################################################



filename <- strsplit(as.character(opt$file),"/")
filename <- sub(as.character(opt$suffix),"",filename[[1]][length(filename[[1]])])
filename <- sub("^_","",filename)
if (opt$outfile != "NULL"){
  filename <- opt$outfile
}

print(filename)

results = read.table(as.character(opt$file),header = T,sep = "\t")

#names(results) = as.character(unlist(results[1,]))
#results = results[-1,]

results = mutate(results, sig=ifelse((results$PValue >0.01 | abs(results$logFC) < 1), "not differential expressed",
                                     ifelse(results$logFC < 0, "down-regulated genes",
                                            "up-regulated genes")))

#filenames <- list.files(path="./", pattern="*.txt")
#names <-substr(filenames,1,18)
#for(i in names){
#  filepath <- file.path("../volcano_plot/",paste(i,"_result_list.txt",sep=""))
#  assign(i, read.delim(filepath,
#                      colClasses=c("character",rep("numeric",5)), header = T,
#                       sep = "\t"))
#}
#out.file<-""

######################################

######################################

theme_paper <- theme(
    # panel.border = element_rect(fill = NA,colour = "black"),
    # panel.grid.major = element_line(colour = "grey88",
    #                                 size = 0.2),
    # panel.grid.minor = element_line(colour = "grey95",
    #                                 size = 0.5),
    # axis.text.x= element_text(vjust = 1,hjust = 1, angle = 45),
    # legend.position = "top",
    # legend.direction = "horizontal",
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    legend.background=element_blank(),
    legend.key = element_rect(fill = NA,colour = NA),
    legend.position = c(0.28, 0.89),
    legend.text = element_text(size = 10,margin = margin(0,0,0,0)),
    legend.title=element_blank(),

    axis.title = element_text(size = 12),
    plot.title = element_text(size = 12),
    axis.text = element_text(size = 12, colour = "black"))


color_points <- function(pval, lfc, q_cut, lfc_cut,upnum, downnum,nonum) {
  # level 1: qval > q_cut
  # level 2: qval < q_cut & lfc < lfc_cut
  # level 3: qval < q_cut & lfc > lfc_cut
  signif_levels <- c(paste0("not differential expressed","(",nonum,")"),
                     paste0("down-regulated genes","(",downnum,")"),
                     paste0("up-regulated genes","(",upnum,")"))
  signif_points <- ifelse((pval > q_cut | abs(lfc) < lfc_cut), signif_levels[1],
                          ifelse(lfc < 0, signif_levels[2],
                                 signif_levels[3]))
  signif_points <- factor(signif_points, levels = signif_levels)
  return(signif_points)
}




volcano_plot <- function(pval, lfc, q_cut, lfc_cut,upnum, downnum,nonum) {
  # Creating figure similar to Figure 1A of Barreiro, Tailleux, et al., 2012.
  signif_points <- color_points(pval, lfc, q_cut, lfc_cut,upnum, downnum,nonum)
  dat <- data.frame(p = -log10(pval), lfc = lfc, signif = signif_points)
  ggplot(dat) + geom_point(aes(x = lfc, y = p, color = signif,shape=signif,alpha=signif,size=signif)) +
    scale_color_manual(values = c("black", "#456A9F", "#FB654A"), drop = FALSE) +
    scale_shape_manual(values = c(1, 16, 16), drop = FALSE) +
    scale_alpha_manual(values = c(0.3, 0.9, 0.9), drop = FALSE) +
    scale_size_manual(values = c(1, 1.5, 1.5), drop = FALSE) +
    labs(title = "Volcano plot", x = expression(paste(log[2], " fold change")),
         y = expression(paste("-", log[10], " p-value"))) +
    theme_bw()+theme_paper
    # theme(legend.title=element_blank(),
    #       legend.direction = "vertical",
    #
    #       legend.title = element_text(size = 12),
    #       legend.text = element_text(size = 12, face = 'bold'),
    #       legend.key = element_rect(fill = 'white'),
    #       legend.key.size = unit(0.4,"cm"),
    #       legend.position = c(0.18, 0.9),
    #
    #       panel.background = element_rect(fill = "white",colour = NA),
    #       panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
    #       panel.grid.major = element_line(size=0.5,colour = "#FFFFFF"),
    #       panel.grid.minor = element_line(size=0.1,colour = "#FFFFFF"))
}



exp_plot <- function(ra, rb, ra_name,rb_name,pval, lfc, q_cut, lfc_cut,upnum, downnum,nonum) {
  # Creating figure similar to Figure 1A of Barreiro, Tailleux, et al., 2012.
  signif_points <- color_points(pval, lfc, q_cut, lfc_cut,upnum, downnum,nonum)
  dat <- data.frame(ra = ra, rb = rb, signif = signif_points)
  ggplot(dat) + geom_point(aes(x = ra, y = rb, color = signif,shape=signif,alpha=signif,size=signif)) +
    scale_color_manual(values = c("black", "#456A9F", "#FB654A"), drop = FALSE) +
    scale_shape_manual(values = c(1, 16, 16), drop = FALSE) +
    scale_alpha_manual(values = c(0.3, 0.9, 0.9), drop = FALSE) +
    scale_size_manual(values = c(1, 1.5, 1.5), drop = FALSE) +
    labs(title = "Exp plot", x = paste("RPKM of ",ra_name),
         y = paste("RPKM of ",rb_name)) +
    # ylim(0,250)+xlim(0,250)+
    theme_bw()+theme_paper
    # theme(legend.title=element_blank(),
    #       legend.direction = "vertical",
    #
    #       legend.title = element_text(size = 12),
    #       legend.text = element_text(size = 12, face = 'bold'),
    #       legend.key = element_rect(fill = 'white'),
    #       legend.key.size = unit(0.4,"cm"),
    #       legend.position = c(0.18, 0.9),
    #
    #       panel.background = element_rect(fill = "white",colour = NA),
    #       panel.border = element_rect(size = 1,colour = "#8B8B8B",fill =NA),
    #       panel.grid.major = element_line(size=0.5,colour = "#FFFFFF"),
    #       panel.grid.minor = element_line(size=0.1,colour = "#FFFFFF"))
}



#+theme_Publication()+ theme(legend.position="none")
# head(volcano_1[[1]])
# sigif <- factor(results$sig,levels = c("not differential expressed","down-regulated genes","up-regulated genes"))
# p1 = ggplot(results) +
#   labs(title = "")+
#   geom_point(alpha=0.8,size=1.2,aes(x = F_C, y = M_C, color = signif,shape=sigif,alpha=signif,size=signif)) + coord_flip()+
#   scale_color_manual(values=c("black", "#456A9F", "#FB654A"))+
#   scale_shape_manual(values=c(1, 16, 16), drop = FALSE)+
#   scale_alpha_manual(values = c(0.3, 1, 1), drop = FALSE) +
#   scale_size_manual(values = c(1, 1.5, 1.5), drop = FALSE) +
#   ylim(0,1000)+xlim(0,1000)
# p1






results.Up <- subset(results, logFC > 1 & PValue <= 0.01) #define Green
results.Up <-mutate(results.Up,"Up")
upnum <- length(results.Up$Gene)
results.No <- subset(results, PValue > 0.01 | abs(logFC) < 1) #define Black
results.No <- mutate(results.No,"Not-sig")
nonum <- length(results.No$Gene)
results.Dn <- subset(results, logFC < -1  & PValue <= 0.01) #define Red
results.Dn <-mutate(results.Dn,"Down")
downnum <- length(results.Dn$Gene)
# colnames(results.Up)<-c("Gene","logFC","logCPM","PValue","sig")
# colnames(results.No)<-c("Gene","logFC","logCPM","PValue","sig")
# colnames(results.Dn)<-c("Gene","logFC","logCPM","PValue","sig")
# results <- rbind(results.Up, results.No, results.Dn)
# results$sig <- as.factor(results$sig)
#########################

colname <- colnames(results[,c(a,b)])
x <- log(results[,a]+1,10)
y <- log(results[,b]+1,10)

Max <- max(max(results[,a]),max(results[,b]))

CorResult <- cor(x,y,method = 'pearson')
CorResult <- round(CorResult,3)
CorResult <- paste("italic(R)==",CorResult,sep='')
CorResult
Max
exp_1 <- exp_plot(results[,a],results[,b],colname[1],colname[2],results$PValue,results$logFC,
                  q_cut = .01, lfc_cut = 1, upnum=upnum, downnum=downnum,nonum=nonum) +
  labs(title = "")+
  # scale_x_continuous(breaks = seq(-8, 8, 2)) +
  # scale_y_continuous(trans = "log10",limits = c(1, Max))+scale_x_continuous(trans = "log10",limits = c(1, Max))
  scale_y_continuous(trans = "log10")+scale_x_continuous(trans = "log10")
if (opt$addcor==1){
  exp_1 <- exp_1 + geom_abline(aes(intercept=0,slope=1),linetype = "dashed",size = 0.8,colour = "gray50")+
    annotate("text",x= 0.1*Max,y=0.6*Max,label = CorResult,size= 4,parse = TRUE)
}

# ylim(0,500)+xlim(0,500)

ggsave(paste(filename,"_exp.pdf",sep=""), width = 130, height = 120, units = "mm")
ggsave(paste(filename,"_exp.png",sep=""), width = 130, height = 120, units = "mm", dpi = 450)

volcano_1 <- volcano_plot(results$PValue,results$logFC,
                          q_cut = .01, lfc_cut = 1, upnum=upnum, downnum=downnum,nonum=nonum) +
  labs(title = "")+
  scale_x_continuous(breaks = seq(-8, 8, 2),limits = c(-8, 8)) +
  ylim(0,30)


######################
# multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
#   library(grid)
#
#   # Make a list from the ... arguments and plotlist
#   plots <- c(list(...), plotlist)
#
#   numPlots = length(plots)
#
#   # If layout is NULL, then use 'cols' to determine layout
#   if (is.null(layout)) {
#     # Make the panel
#     # ncol: Number of columns of plots
#     # nrow: Number of rows needed, calculated from # of cols
#     layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
#                      ncol = cols, nrow = ceiling(numPlots/cols))
#   }
#
#   if (numPlots==1) {
#     print(plots[[1]])
#
#   } else {
#     # Set up the page
#     grid.newpage()
#     pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
#
#     # Make each plot, in the correct location
#     for (i in 1:numPlots) {
#       # Get the i,j matrix positions of the regions that contain this subplot
#       matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
#
#       print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
#                                       layout.pos.col = matchidx$col))
#     }
#   }
# }
##########################

########################## reformated by JieHuang
# multiplot()
#grid.arrange(b1, b2, b3,b4, nrow=2, ncol=2)

ggsave(paste(filename,"_DEG.pdf",sep=""), width = 130, height = 120, units = "mm")
ggsave(paste(filename,"_DEG.png",sep=""), width = 130, height = 120, units = "mm", dpi = 450)

