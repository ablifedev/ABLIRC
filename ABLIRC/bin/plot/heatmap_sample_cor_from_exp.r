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
#
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("stats"))

option_list <- list(
  make_option(c("-f", "--file"),action = "store",type = "character",
              help = "The Input file"),
  make_option(c("-s","--sample"),action = "store",type = "character",
              help = "The sample file"),
  make_option(c("-b","--start"),action = "store",type = "integer",default = 1,
              help = "appoint the column of start ; default = 1"),
  make_option(c("-e","--end"),action = "store",type = "integer",default = -1,
              help = "appoint the column of end; default = -1"),
  make_option(c("-n","--filename"),action = "store",type = "character",default="Sample_correlation",
              help = "The filename of the picture ; default = test.pdf"),
  make_option(c("-o", "--outdir"),action = "store",type = "character",default = "./",
              help = "The outdir;default = ./")
)
opt <- parse_args(OptionParser(option_list = option_list))
start <- as.numeric(opt$start)
end <- as.numeric(opt$end)

# library(cluster)
# library(Biobase)
# library(qvalue)
library("corrplot")
NO_REUSE = F

# opt$file = "Sex_specific_lncRNA_value.txt"
# opt$file = "exp.txt"

# # get the filename to use later
filename <- strsplit(opt$file,"/")[[1]]
filename <- filename[length(filename)]
filename <- sub('.txt','',filename)

# # try to reuse earlier-loaded data if possible

# print('Reading matrix file.')
primary_data = read.table(opt$file, header=T, com='', sep="\t", row.names=1, check.names=F)
# primary_data = read.table("Sample_correlation.dat", header=T, com='', sep="\t", row.names=1, check.names=F)


if(end> 0){
  primary_data <- primary_data[,start:end]
}
primary_data = as.matrix(primary_data)
primary_data = log2(primary_data+1)
data = primary_data

sample_cor = cor(data, method='pearson', use='pairwise.complete.obs')
# sample_cor = cor(data, method='pearson')
# round(sample_cor,2)
cat(c('Gene\t'),file=paste(opt$filename,".xls",sep=''))

write.table(sample_cor, file=paste(opt$filename,".xls",sep=''), quote=F, append=T, sep='\t')
data <- sample_cor
# # sample_dist = dist(t(data), method='euclidean')
# # hc_samples = hclust(sample_dist, method='complete')
# col <- colorRampPalette(c("#67001F", "#B2182B", "#D6604D",
#                           "#F4A582", "#FDDBC7", "#FFFFFF", "#D1E5F0", "#92C5DE",
#                           "#4393C3", "#2166AC", "#053061","#67001F", "#B2182B", "#D6604D",
#                           "#F4A582", "#FDDBC7", "#FFFFFF", "#D1E5F0", "#92C5DE",
#                           "#4393C3", "#2166AC", "#053061","#67001F", "#B2182B", "#D6604D",
#                           "#F4A582", "#FDDBC7", "#FFFFFF", "#D1E5F0", "#92C5DE",
#                           "#4393C3", "#2166AC", "#053061","#67001F", "#B2182B", "#D6604D",
#                           "#F4A582", "#FDDBC7", "#FFFFFF", "#D1E5F0", "#92C5DE",
#                           "#4393C3", "#2166AC", "#053061"))(200)
# min <- min(sample_cor)
# corrplot(sample_cor, type="upper", order="hclust", hclust.method="complete",col=col,tl.srt=45,cl.lim=c(min,1))


# data("ALL")
# library(limma)
# eset<-ALL[,ALL$mol.biol %in% c("BCR/ABL","ALL1/AF4")]
# f<-factor(as.character(eset$mol.biol))
# design<-model.matrix(~f)

# selected  <- p.adjust(fit$p.value[, 2]) <0.001

# data<-exprs(esetSel)

library(pheatmap)
library("RColorBrewer")
library(grid)





# data[lower.tri(data)]=NA



# triangle heatmap
o = rownames(data)
sample_dist = dist(t(primary_data), method='euclidean')
hc = hclust(sample_dist, method='complete')
# hc = hclust(as.dist(1 - data))
data = data[hc$order, hc$order]
# data[lower.tri(data)] = NA
data = data[o, o]
data

## Edit body of pheatmap:::draw_colnames, customizing it to your liking
# draw_colnames_45 <- function (coln, ...) {
#     m = length(coln)
#     x = (1:m)/m - 1/2/m
#     grid.text(coln, x = x, y = unit(0.96, "npc"), vjust = .5,
#         hjust = 1, rot = 45, gp = gpar(...)) ## Was 'hjust=0' and 'rot=270'
# }

# ## 'Overwrite' default draw_colnames with your own version
# assignInNamespace(x="draw_colnames", value="draw_colnames_45",
# ns=asNamespace("pheatmap"))


# scaleyellowred <- colorRampPalette(c("#08519c","#3182bd","#ffffff","#e6550d","#e6550d","#a63603","#a63603"),space = "rgb")(500)
# scaleyellowred <- colorRampPalette(c("#08519c","#3182bd","#ffffff","#e6550d","#e6550d","#e6550d","#a63603","#a63603","#a63603"),space = "rgb")(500)


rowcount <- nrow(data)

if (rowcount>7){
  pheatmap(data, cluster_col = hc, cluster_row = hc,border_color="white",show_colnames=T,cellwidth = 30, cellheight = 30, fontsize=27,filename = paste(opt$filename,".pdf",sep=''),display_numbers = FALSE)

  pheatmap(data, cluster_col = hc, cluster_row = hc,border_color="white",show_colnames=T,cellwidth = 30, cellheight = 30, fontsize=27,filename = paste(opt$filename,".png",sep=''),display_numbers = FALSE)
}

if (rowcount<=7){
  pheatmap(data, cluster_col = hc, cluster_row = hc,border_color="white",show_colnames=T,fontsize=20,filename = paste(opt$filename,".pdf",sep=''),display_numbers = FALSE,width = 8, height = 7)

  pheatmap(data, cluster_col = hc, cluster_row = hc,border_color="white",show_colnames=T,fontsize=20,filename = paste(opt$filename,".png",sep=''),display_numbers = FALSE,width = 8, height = 7)
}





# correlation


# gene heatmap







# # data = log2(data+1)
# data[,c(1,2,3,4,5)] <- data[,c(1,2,3,4,5)]/data[,1]
# #deg
# col.pal <- brewer.pal(9,"Blues")
# # colorRampPalette is in the RColorBrewer package.  This creates a colour palette that shades from light yellow to red in RGB space with 100 unique colours
# scaleyellowred <- colorRampPalette(c("lightyellow","pink", "red"),space = "rgb")(500)



# color.map <- function(mol.biol) { if (mol.biol=="ALL1/AF4") 1 else 2 }
# patientcolors <- unlist(lapply(esetSel$mol.bio, color.map))
# hc<-hclust(dist(t(data)))
# dd.col<-as.dendrogram(hc)
# groups <- cutree(hc,k=7)
# annotation<-data.frame(Var1=factor(patientcolors,labels=c("class1","class2")),Var2=groups)

# Var1 = c("navy", "skyblue")
# Var2 = c("snow", "steelblue")
# names(Var1) = c("class1", "class2")
# ann_colors = list(Var1 = Var1, Var2 = Var2)


