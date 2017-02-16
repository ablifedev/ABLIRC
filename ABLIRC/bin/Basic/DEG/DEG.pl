#!/usr/bin/perl -w

my $ver = "1.0.0";

use strict;
use warnings;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
my @bin=split(/\//,$Bin);
my $len=scalar(@bin);
my $Bin=join('/',@bin[0..$len-3]);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);
use Pod::Usage;


=head1 Description

Program: DEG.pl

Copyright (c): ABLife 2015

Writer: ChengChao <chaocheng@ablife.cc>

Version: 1.0

功能：利用TCC包进行各种Differential expressed (Gene|miRNA|species)分析，
目前可以进行的DEG分析有：

=head1 Usage

perl DEG.pl [options] > DEG.log

    -config  *.scafSeq file output by SOAPdenovo, required

    -reads   minumum length of scaffold to output, default 0

    -TPM     minumum length of singleton to output, default 0

    -type    minumum length of singleton to output, default 0

    -rep     compare between group with repetation

    -target  gene annotation

    -h       output help information

=cut

my $help = 0;
my $rep = 0;
my ($config, $EG_reads, $EG_TPM, $target);
my $outdir = "./";
my $degtype = "metaphlan";
# my %opts;
GetOptions (
    "config:s"=>\$config,
    "reads:s"=>\$EG_reads,
    "TPM:s"=>\$EG_TPM,
    "type:s"=>\$degtype,
    "rep"=>\$rep,
    "target:s"=>\$target,
    "od:s"=>\$outdir,
    'h|help|?' => \$help
) or die `pod2text $0` ;

die `pod2text $0` if $help;

## print the command
listToString();
sub listToString{

    my $rVal = '';
    foreach my $a (@ARGV){
        $rVal .= $a . ' ';
    }
    print "Command:\nperl $0 $rVal\n\n";
}

if (! -f $config) {
    print "\n[Error] $config does not exist.\n\n";
    die `pod2text $0`;
}
if (! -f $EG_reads) {
    print "\n[Error] $EG_reads does not exist.\n\n";
    die `pod2text $0`;
}
if (! -f $EG_TPM) {
    print "\n[Error] $EG_TPM does not exist.\n\n";
    die `pod2text $0`;
}

$EG_reads = &AbsolutePath("file",$EG_reads);
$EG_TPM = &AbsolutePath("file",$EG_TPM);


#############Time_start#############
my $start_time = time();
my $Time_Start;
$Time_Start = sub_format_datetime( localtime( time() ) );
print "\nStart Time :[$Time_Start]\n\n";
####################################

my %s_num = (); #number of sample name
my %list_num = (); #number string of list name
my %list_count = (); #number string of list name

my %ConfigOption = ();
&Get_config_option($config,\%ConfigOption);
my $annofile = "";
if (exists($ConfigOption{"Target"})) {
	$annofile = $ConfigOption{"Target"};
}
if (defined($target) && $target ne "-") {
	$annofile = $target;
}
if (defined($ConfigOption{"rep"}) && $ConfigOption{"rep"} eq "y") {
	$rep = 1;
}

print $annofile,"anno\n";

my $method = $ConfigOption{"METHOD"};
my $p_value = $ConfigOption{"PVALUE"};
my $FC = $ConfigOption{"FC"};
my $log = $ConfigOption{"LOG"};

my $current_dir = `pwd`;
chomp($current_dir);
$outdir = "$current_dir/$outdir" if ( $outdir !~ /^\/|\~/ );
print $outdir,"\n";
`mkdir -p $outdir`;
# chdir($outdir)


my @sample_name = ();
my $sample_num = Load_RNA_seq( \%ConfigOption, $outdir, $EG_reads, $EG_TPM, \@sample_name );    #load RNA seq file
print scalar(@sample_name),"\t",join("\t",@sample_name),"\n";
#exit;

if (not $rep){
    &DEG_calculate_nonrep(\%ConfigOption,$EG_reads,$EG_TPM);
}else{
    &DEG_calculate(\%ConfigOption,$EG_reads,$EG_TPM);
}

#exit;
#`perl $Bin/Select_gene_symbol.pl -indir $outdir `;
# if (exists($ConfigOption{"GeneAnno"})) {
# 	my $annofile = $ConfigOption{"GeneAnno"};
# 	`cd $outdir && find ./ -name '*.addexp' | perl -ne 'chomp;print "cd $outdir && perl /users/ablife/ablife-perl/public/exp_add_anno.pl -exp \$_ -anno $annofile & \\n";' > anno.sh `;
# 	`cd $outdir && sh anno.sh`;
# }

if ($annofile ne "") {
	`cd $outdir && find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "cd $outdir && perl $Bin/public/exp_add_anno.pl -exp \$_ -anno $annofile -annonum auto -o \$name & \\n";' > anno.sh `;
	`cd $outdir && sh anno.sh`;
}else{
	`cd $outdir && find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "cd $outdir && mv \$_ \$name & \\n";' > anno.sh `;
	`cd $outdir && sh anno.sh`;
}

if (exists($ConfigOption{"CODEG"})) {
	&Co_DEG_analysis(\%ConfigOption, $outdir);
}

if (exists($ConfigOption{"DIDEG"})) {
	&Di_DEG_analysis(\%ConfigOption, $outdir);
}

###############Sub###########

sub Get_config_option {
	my ($file,$hash_ref) = @_;
	my $start_flag = 0;
	#print $file,"\n";
	my $minnum=10000;
	open (CONFIG,"<$file") or die "Can't open $file!\n";
	while (<CONFIG>) {
		chomp;
		next if(/^\#/);
		next if(/^\/\/\//);
		next if(/^\s*$/);
		s/\/\/\/.*//g;
		s/\r//g;		#chomp the \r character
		if(/^\[/){
			$start_flag=0;
		}
		if(/^\[gc|sample\]/){
			$start_flag=1;
		}
		if(/^\[\[ablife:(\w+)\]\]/){
			my $tag = $1;
			if($tag eq "config" || $tag eq "sample" || $tag eq $degtype){
				print $_,"\n";
				$start_flag=1;
			}
			next;
		}elsif(/^\[module:(\w+)\]/){
            my $tag = $1;
            print $tag,"\n";
            if($tag eq "gc" || $tag eq "sample" || $tag eq $degtype){
                # print $_,"\n";
                $start_flag=1;
            }
            next;
        }
		if($start_flag==0){
			next;
		}
		print $_,"\n";
		my @line = split(/\t|\s*\=\s*/);
		if ($line[0] =~ /^sample/i) {
			$line[0]=~s/SAMPLE//i;
			if ($line[0]<$minnum){$minnum=$line[0];}
			@{$hash_ref->{"SAMPLE"}->{$line[0]}} = split(":",$line[1]);
			my $sample_name = $hash_ref->{"SAMPLE"}->{$line[0]}->[0];
			$s_num{$sample_name}=&select_index($EG_reads,$sample_name)+1;
		} elsif ($line[0] =~ /^group/i) {
			@{$hash_ref->{"GROUP"}->{$line[0]}} = split(":",$line[1]);
		} elsif ($line[0] =~ /^LIST/i) {
			@{$hash_ref->{"LIST"}->{$line[0]}} = split(":",$line[1]);
			my $listname = $hash_ref->{"LIST"}->{$line[0]}->[1];
			my $listsample = $hash_ref->{"LIST"}->{$line[0]}->[0];
			my @listarray = split(/,/,$listsample);
			my $firstnum = $s_num{$listarray[0]};
			$list_num{$listname}=$firstnum;
			for(my $i=1;$i<scalar(@listarray);$i++){
				$list_num{$listname}.=",".$s_num{$listarray[$i]};
			}
			$list_count{$listname}=scalar(@listarray);
			print $listname,"\t",$list_count{$listname},"\t",$list_num{$listname},"\n";
		} elsif ($line[0] =~ /^codeg/i) {
			@{$hash_ref->{"CODEG"}->{$line[0]}} = split(":",$line[1]);
		} elsif ($line[0] =~ /^dideg/i) {
			@{$hash_ref->{"DIDEG"}->{$line[0]}} = split(":",$line[1]);
		} else {
			$hash_ref->{$line[0]} = $line[1];
		}
	}
	if ($minnum != 1){die "sample num should start with 1!\n";}
	close(CONFIG);
}



sub Load_RNA_seq {    #&Load_RNA_seq(\@RNA_arrReads,$outdir,$EG_files)
	my ($option_ref,$outdir,$EG_reads,$EG_TPM,$sample_name) = @_;

	my $sample_num = 0;

	foreach my $sample (sort keys %{$option_ref->{"SAMPLE"}}) {    #load the RNA seq of every sample
		$sample_num++;
	}
	my $index1 = 2;
	my $index2 = 1 + $sample_num;
	print $index1,"\t",$index2,"\n";
	# print $outdir,"\n";
	# `R --slave </users/ablife/ablife-R/Sample_correlation.r --args $EG_TPM $index1 $index2 $outdir`;
	return $sample_num;
}


sub DEG_calculate_nonrep {
    my ($option_ref, $reads_file, $RPKM_file) = @_;
    my $index1 = 2;
    my $index2 = 1 + $sample_num;
    #`R --slave </users/chend/work/R/RNA-Seq/Sample_correlation.r --args $RPKM_file $index1 $index2 $outdir`;
    foreach my $group (sort keys %{$option_ref->{"GROUP"}}) {
        chdir($outdir);
        my $sample1 = $option_ref->{"GROUP"}->{$group}->[0];
        my $sample2 = $option_ref->{"GROUP"}->{$group}->[1];
        my $test_index = &select_index($EG_reads,$sample1)+1;
        my $control_index = &select_index($EG_reads,$sample2)+1;
        my $edgeR_list_num = $test_index.",".$control_index;
        print $sample1,"_vs_",$sample2,"\n",$edgeR_list_num,"\n";

        print "cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $test_index -c $control_index -o $outdir\n";
        `cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $test_index -c $control_index -o $outdir`;

        my $dir = $sample1."_vs_".$sample2."_".$option_ref->{"METHOD"}."_".$option_ref->{"PVALUE"}."_".$option_ref->{"FC"};
        `mkdir -p $outdir/$dir`;    #make the out direcotry
        $dir = &AbsolutePath("dir","$outdir/$dir");     #the absolute path of out directory
        print $dir,"\n";
        &make_TCC_script_for_nonrep($edgeR_list_num,$dir);
        if ($option_ref->{"METHOD"} ne "edgeR") {
            print "cmd: cat $dir/_tcc.r | R --slave --args $reads_file $RPKM_file ".$option_ref->{"PVALUE"}." ".$option_ref->{"FC"}." "."$sample1 $sample2 $dir \n";
            `cat $dir/_tcc.r | R --slave --args $reads_file $RPKM_file $option_ref->{"PVALUE"} $option_ref->{"FC"} $sample1 $sample2 $dir `;
            # &Add_Exp_to_DEG($RPKM_file,$sample1,$sample2,$dir);
        } elsif ($option_ref->{"METHOD"} eq "DESeq") {

        } else {
            die"You choose the wrong method to calculate DEG!\n";
        }
        chdir($dir);
        &AddExp($RPKM_file,$edgeR_list_num,$dir);
        my $comp = "$sample1\_vs_$sample2";
		`Rscript $Bin/plot/volcano.r -f \_$comp\_result_list_add_exp.txt -o $dir`;
        # if ($option_ref->{"METHOD"} eq "edgeR") {
        #   `cat /users/chend/work/R/RNA-Seq/edgeR_single.r | R --slave --args $reads_file $RPKM_file $option_ref->{"PVALUE"} $option_ref->{"FC"} $index1 $index2 $dir`;
        #   &Add_Exp_to_DEG($RPKM_file,$sample1,$sample2,$dir);
        # } elsif ($option_ref->{"METHOD"} eq "DESeq") {

        # } else {
        #   die"You choose the wrong method to calculate DEG!\n";
        # }
        #chdir($dir);
    }
    chdir($outdir);
}



sub DEG_calculate {
	my ($option_ref, $reads_file, $RPKM_file) = @_;
	my $index1 = 2;
	my $index2 = 1 + $sample_num;
	#`R --slave </users/chend/work/R/RNA-Seq/Sample_correlation.r --args $RPKM_file $index1 $index2 $outdir`;
	foreach my $group (sort keys %{$option_ref->{"GROUP"}}) {
		chdir($outdir);
		my $sample1 = $option_ref->{"GROUP"}->{$group}->[0];
		my $sample2 = $option_ref->{"GROUP"}->{$group}->[1];
		my $edgeR_list_num = $list_num{$sample2}.",".$list_num{$sample1};
		my $edgeR_group_name = "1";
		for (my $i=1;$i<$list_count{$sample2};$i++){
			$edgeR_group_name.=","."1";
		}
		for (my $i=0;$i<$list_count{$sample1};$i++){
			$edgeR_group_name.=","."2";
		}
		print $sample1,"_vs_",$sample2,"\n",$edgeR_list_num,"\n",$edgeR_group_name,"\n";

		my @random1 = split(",",$list_num{$sample1});
		my @random2 = split(",",$list_num{$sample2});
		print (@random1,"\t",@random2,"\n");
		my $index1_random1 = $random1[0];
		my $index2_random1 = $random1[1];
		my $index1_random2 = $random2[0];
		my $index2_random2 = $random2[1];
		`cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $index1_random1 -c $index2_random1 -o $outdir`;
		`cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $index1_random2 -c $index2_random2 -o $outdir`;
		`cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $index1_random1 -c $index1_random2 -o $outdir`;
		`cd $outdir && Rscript $Bin/plot/Cor_line.r -f $RPKM_file -l $log -s $index2_random1 -c $index2_random2 -o $outdir`;

		# `cat /users/chend/work/R/RNA-Seq/Cor_single.r | R --slave --args $RPKM_file $log $index1 $index2 $outdir`;
		my $dir = $sample1."_vs_".$sample2."_".$option_ref->{"METHOD"}."_".$option_ref->{"PVALUE"}."_".$option_ref->{"FC"};
		`mkdir -p $outdir/$dir`;	#make the out direcotry
		$dir = &AbsolutePath("dir","$outdir/$dir");		#the absolute path of out directory
		print $dir,"\n";
		&make_TCC_script_for_rep($edgeR_list_num,$edgeR_group_name,$dir);
		if ($option_ref->{"METHOD"} ne "edgeR") {
			print "cmd: cat $dir/_tcc_replicate.r | R --slave --args $reads_file $RPKM_file ".$option_ref->{"PVALUE"}." ".$option_ref->{"FC"}." "."$sample1 $sample2 $dir \n";
			`cat $dir/_tcc_replicate.r | R --slave --args $reads_file $RPKM_file $option_ref->{"PVALUE"} $option_ref->{"FC"} $sample1 $sample2 $dir `;
			# &Add_Exp_to_DEG($RPKM_file,$sample1,$sample2,$dir);
		} elsif ($option_ref->{"METHOD"} eq "DESeq") {

		} else {
			die"You choose the wrong method to calculate DEG!\n";
		}
		chdir($dir);
		&AddExp($RPKM_file,$edgeR_list_num,$dir);
		# if ($option_ref->{"METHOD"} eq "edgeR") {
		# 	`cat /users/chend/work/R/RNA-Seq/edgeR_single.r | R --slave --args $reads_file $RPKM_file $option_ref->{"PVALUE"} $option_ref->{"FC"} $index1 $index2 $dir`;
		# 	&Add_Exp_to_DEG($RPKM_file,$sample1,$sample2,$dir);
		# } elsif ($option_ref->{"METHOD"} eq "DESeq") {

		# } else {
		# 	die"You choose the wrong method to calculate DEG!\n";
		# }
		#chdir($dir);
	}
	chdir($outdir);
}

sub AddExp {
	my ($RPKM_file,$edgeR_list_num,$dir)=@_;
	my @g = split(/,/,$edgeR_list_num);
	my $samplenum = scalar(@g);
	`cd $dir && cut -f 1,$edgeR_list_num $RPKM_file > exp.temp`;
	`cd $dir && find ./ -name "*DEG.txt" -or -name "*list.txt" | perl -ne 'chomp;\$name = \$_; \$name=~s/.txt//;print "cd $dir && perl $Bin/public/exp_add_anno.pl -exp \$_ -anno normalized.count.txt -o \$name\\_add_exp.txt -rc 0 -annonum auto \\n";' > addexp.sh `;
	`cd $dir && sh addexp.sh && rm -rf exp.temp`;
}


# A data frame object containing following fields:
# gene_id character vector indicating the id of the count unit, usually gene.
# a.value numeric vector of average expression level on log2 scale (i.e., A-value) for each
#         gene across the compared two groups. It corresponds to the x coordinate in the
#         M-A plot.
# m.value numeric vector of fold-change on log2 scale (i.e., M-value) 
#         for each gene between the two groups compared. It corresponds to the y coordinate in the M-A plot.
# p.value numeric vector of p-value.
# q.value numeric vector of q-value calculated based on the p-value using the p.adjust function with default parameter settings.
# rank    numeric vector of gene rank in order of the p-values.
# estimatedDEG numeric vector consisting of 0 or 1 depending on whether each gene is classified as non-DEG or DEG. The threshold for classifying DEGs or non-DEGs is preliminarily given when performing estimateDE.




sub make_TCC_script_for_rep {
	my ($edgeR_list_num,$edgeR_group_name,$dir)=@_;
	my $r_file = $dir."/_tcc_replicate.r";
	open ROUT ,">$r_file" or die "can't open $r_file!\n";
	print ROUT <<EOF;
rm(list=ls())
library(TCC)
args <- commandArgs(trailingOnly = TRUE)	#get the arguments from the command line
if (length(args) < 7) {
	stop('Your input arguments is wrong!\\n
		args1:\\t the reads file\\n
		args2:\\t the RPKM file\\n
		args3:\\t the P-value number\\n
		args4:\\t the fold change value\\n
		args5:\\t test sample name\\n
		args6:\\t control sample name\\n
		args7:\\t the out directory\\n\\n'
	)
} else {
	fileReads <- args[1]
	fileRPKM <- args[2]
	p.value <- as.numeric(args[3])
	foldChange <- as.numeric(args[4])
	test <- args[5]
	control <- args[6]
	outdir <- args[7]
}
RawData <- read.table(fileReads,header=T,sep="\\t")
columnNum <- ncol(RawData)     #the column count of data array
columnName <- colnames(RawData)    #the name of the colums
setwd(outdir)
rownames(RawData) <- RawData[,1]	#replace rownames by gene ID,very inportant
data <- RawData

EOF
	print ROUT "sample \<- data\[,c\($edgeR_list_num\)\] \n";
	print ROUT "group \<- c\($edgeR_group_name\) \n";
	print ROUT <<EOF;
tcc <- new("TCC",sample,group)
tcc <- calcNormFactors(tcc, norm.method = "tmm", test.method = "edger",iteration = 3, FDR = 0.1, floorPDEG = 0.05)
tcc <- estimateDE(tcc, test.method = "edger", FDR = 0.1)
normalized.count <- getNormalizedData(tcc)
summary(normalized.count)
de.com <- getResult(tcc, sort = TRUE)
colnames(de.com)[1]<-columnName[1]
de <- de.com[(de.com\$p.value <= p.value),]
de.Sig <- de[(abs(de\$m.value) > log2(foldChange)),]
de.Sig.down <- de.Sig[(de.Sig\$m.value < -log2(foldChange)),]
de.Sig.up <- de.Sig[(de.Sig\$m.value > log2(foldChange)),]
# detags.com <- rownames(de.com\$table[(de.com\$table\$PValue <= p.value &
# 	(de.com\$table\$logFC > log2(foldChange) |
# 	(de.com\$table\$logFC < -log2(foldChange)))),]
# )

png(file =paste(test,'_vs_',
      control,'_',"DEG.png",sep=''),
      height=600,width=600
)
par(mar=c(6.1,6.1,6.1,6.1))
plot(tcc)

# plotSmear(List, de.tags = detags.com,pair = c("Test","Control"),
#       main = paste(test,'/',control,' DEG(red)',sep=''),
#       cex.main=3,cex.lab=2.5,cex.axis=2,cex=0.3,
#       font.axis=2,font.lab=2,lty=3,
#       ylim=c(-6,6)
# )
dev.off()
write.table(de.com,file=paste('_',test,'_vs_',control,'_result_list.txt',sep=''),
		append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig,file=paste('_',test,'_vs_',control,'_Sig_DEG.txt',sep=''),
		append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig.up,file=paste('_',test,'_vs_',control,'_Up_DEG.txt',sep=''),
		append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig.down,file=paste('_',test,'_vs_',control,'_Down_DEG.txt',sep=''),
		append=T,quote=F,row.names = FALSE,sep='\\t')
cat(c(columnName[1],'\\t'),file='normalized.count.txt')
write.table(normalized.count,file='normalized.count.txt',
		append=T,quote=F,row.names = TRUE,sep='\\t')
EOF
}

sub make_TCC_script_for_nonrep {
    my ($edgeR_list_num,$dir)=@_;
    my $r_file = $dir."/_tcc.r";
    open ROUT ,">$r_file" or die "can't open $r_file!\n";
    print ROUT <<EOF;
rm(list=ls())
library(TCC)
args <- commandArgs(trailingOnly = TRUE)    #get the arguments from the command line
if (length(args) < 7) {
    stop('Your input arguments is wrong!\\n
        args1:\\t the reads file\\n
        args2:\\t the RPKM file\\n
        args3:\\t the P-value number\\n
        args4:\\t the fold change value\\n
        args5:\\t test sample name\\n
        args6:\\t control sample name\\n
        args7:\\t the out directory\\n\\n'
    )
} else {
    fileReads <- args[1]
    fileRPKM <- args[2]
    p.value <- as.numeric(args[3])
    foldChange <- as.numeric(args[4])
    test <- args[5]
    control <- args[6]
    outdir <- args[7]
}
RawData <- read.table(fileReads,header=T,sep="\\t")
columnNum <- ncol(RawData)     #the column count of data array
columnName <- colnames(RawData)    #the name of the colums
setwd(outdir)
rownames(RawData) <- RawData[,1]    #replace rownames by gene ID,very inportant
data <- RawData

EOF
    print ROUT "sample \<- data\[,c\($edgeR_list_num\)\] \n";
    print ROUT "group \<- c\(1,2\) \n";
    print ROUT <<EOF;
tcc <- new("TCC",sample,group)
tcc <- calcNormFactors(tcc, norm.method = "deseq2", test.method = "deseq2",iteration = 3, FDR = 0.1, floorPDEG = 0.05)
tcc <- estimateDE(tcc, test.method = "deseq2", FDR = 0.1)
normalized.count <- getNormalizedData(tcc)
summary(normalized.count)
de.com <- getResult(tcc, sort = TRUE)
colnames(de.com)[1]<-columnName[1]
de <- de.com[(de.com\$p.value <= p.value),]
de.Sig <- de[(abs(de\$m.value) > log2(foldChange)),]
de.Sig.down <- de.Sig[(de.Sig\$m.value < -log2(foldChange)),]
de.Sig.up <- de.Sig[(de.Sig\$m.value > log2(foldChange)),]
# detags.com <- rownames(de.com\$table[(de.com\$table\$PValue <= p.value &
#   (de.com\$table\$logFC > log2(foldChange) |
#   (de.com\$table\$logFC < -log2(foldChange)))),]
# )

png(file =paste(test,'_vs_',
      control,'_',"DEG.png",sep=''),
      height=600,width=600
)
par(mar=c(6.1,6.1,6.1,6.1))
plot(tcc)

# plotSmear(List, de.tags = detags.com,pair = c("Test","Control"),
#       main = paste(test,'/',control,' DEG(red)',sep=''),
#       cex.main=3,cex.lab=2.5,cex.axis=2,cex=0.3,
#       font.axis=2,font.lab=2,lty=3,
#       ylim=c(-6,6)
# )
dev.off()
write.table(de.com,file=paste('_',test,'_vs_',control,'_result_list.txt',sep=''),
        append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig,file=paste('_',test,'_vs_',control,'_Sig_DEG.txt',sep=''),
        append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig.up,file=paste('_',test,'_vs_',control,'_Up_DEG.txt',sep=''),
        append=T,quote=F,row.names = FALSE,sep='\\t')
write.table(de.Sig.down,file=paste('_',test,'_vs_',control,'_Down_DEG.txt',sep=''),
        append=T,quote=F,row.names = FALSE,sep='\\t')
cat(c(columnName[1],'\\t'),file='normalized.count.txt')
write.table(normalized.count,file='normalized.count.txt',
        append=T,quote=F,row.names = TRUE,sep='\\t')
EOF
}


sub make_edgeR_script {
	my ($edgeR_list_num,$edgeR_group_name,$dir)=@_;
	my $r_file = $dir."/_edgeR_single_replicate.r";
	open ROUT ,">$r_file" or die "can't open $r_file!\n";
	print ROUT <<EOF;
rm(list=ls())
library('edgeR')
args <- commandArgs(trailingOnly = TRUE)	#get the arguments from the command line
if (length(args) < 7) {
	stop('Your input arguments is wrong!\\n
		args1:\\t the reads file\\n
		args2:\\t the RPKM file\\n
		args3:\\t the P-value number\\n
		args4:\\t the fold change value\\n
		args5:\\t test sample name\\n
		args6:\\t control sample name\\n
		args7:\\t the out directory\\n\\n'
	)
} else {
	fileReads <- args[1]
	fileRPKM <- args[2]
	p.value <- as.numeric(args[3])
	foldChange <- as.numeric(args[4])
	test <- args[5]
	control <- args[6]
	outdir <- args[7]
}
RawData <- read.table(fileReads,header=T,sep="\\t")
setwd(outdir)
rownames(RawData) <- RawData[,1]	#replace rownames by gene ID,very inportant
data <- RawData
columnNum <- ncol(data)		#the column count of data array
columnName <- colnames(data)	#the name of the colums
EOF
	print ROUT "sample \<- data\[,c\($edgeR_list_num\)\] \n";
	print ROUT "group \<- c\($edgeR_group_name\) \n";
	print ROUT <<EOF;
List <- DGEList(counts=sample,group = group)		#make a DGE list format,very important
Factor <- calcNormFactors(List)		# normalize the List
d <- estimateCommonDisp(Factor)		#estimate Common disperation
group <- rev(group);
de.com <- exactTest(d)			#Testing for differential expression
de <- de.com\$table[(de.com\$table\$PValue <= p.value),]
maxFC <- max(abs(de\$logFC))
de.Sig <- de[(abs(de\$logFC) > log2(foldChange)),]
de.Sig.down <- de.Sig[(de.Sig\$logFC < -log2(foldChange)),]
de.Sig.up <- de.Sig[(de.Sig\$logFC > log2(foldChange)),]
detags.com <- rownames(de.com\$table[(de.com\$table\$PValue <= p.value &
	(de.com\$table\$logFC > log2(foldChange) |
	(de.com\$table\$logFC < -log2(foldChange)))),]
)

png(file =paste(test,'_vs_',
		control,'_',"DEG.png",sep=''),
		height=600,width=600
)
par(mar=c(6.1,6.1,6.1,6.1))

plotSmear(List, de.tags = detags.com,pair = c("Test","Control"),
		main = paste(test,'/',control,' DEG(red)',sep=''),
		cex.main=3,cex.lab=2.5,cex.axis=2,cex=0.3,
		font.axis=2,font.lab=2,lty=3,
		ylim=c(-6,6)
)
dev.off()
cat(c('Gene','\\t'),file=paste('_',test,'_vs_',control,'_result_list.txt',sep=''))
write.table(de.com\$table,file=paste('_',test,'_vs_',control,'_result_list.txt',sep=''),
		append=T,quote=F,sep='\\t')
cat(c('Gene','\\t'),file=paste('_',test,'_vs_',control,'_Sig_DEG.txt',sep=''))
write.table(de.Sig,file=paste('_',test,'_vs_',control,'_Sig_DEG.txt',sep=''),
		append=T,quote=F,sep='\\t')
cat(c('Gene','\\t'),file=paste('_',test,'_vs_',control,'_Up_DEG.txt',sep=''))
write.table(de.Sig.up,file=paste('_',test,'_vs_',control,'_Up_DEG.txt',sep=''),
		append=T,quote=F,sep='\\t')
cat(c('Gene','\\t'),file=paste('_',test,'_vs_',control,'_Down_DEG.txt',sep=''))
write.table(de.Sig.down,file=paste('_',test,'_vs_',control,'_Down_DEG.txt',sep=''),
		append=T,quote=F,sep='\\t')
EOF
}

sub Co_DEG_analysis {    #&Select_co_DEG($method,$outdir,$file1,$file2,$i,$j,\%DEG_method)
	my ($option_ref, $outdir) = @_;
	chdir($outdir);
	`mkdir -p co_DEG` if ( !-d "co_DEG");
	my $codeg_dir = $outdir."/co_DEG";
	foreach my $coDEG (sort keys %{$option_ref->{"CODEG"}}) {
		my @Sig_file = ();
		my @Up_file = ();
		my @Down_file = ();
		my @Group_name = ();
		chdir($outdir);
		#print join(":",@{$option_ref->{"CODEG"}->{$coDEG}}),"\n";
		#print `pwd`;
		$outdir = &AbsolutePath("dir",$outdir);
		foreach my $group (@{$option_ref->{"CODEG"}->{$coDEG}}) {
			push @Group_name, $group;
			opendir(DH,$outdir) or die "$!\n";
			foreach my $element (readdir DH) {
				if (-d $element) {
					if ($element =~ /$group/i ) {
						opendir(DIR,$element) or die "$!\n";
						# print $outdir."/".$element,"\n";
						foreach my $file (readdir DIR) {
							next if $file !~ /^_/;
							if ($file =~ /_Sig_DEG.txt$/i) {
								push @Sig_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							}elsif ($file =~ /_Down_DEG.txt$/i) {
								push @Down_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							}elsif ($file =~ /_Up_DEG.txt$/i) {
								push @Up_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							} else {
								next;
							}
						}
					}
				} else {
					next;
				}
			}
			close(DH);
		}

		# print join("\n",@Sig_file),"\n";
		chdir("co_DEG");
		my $co_dir = join("_and_",@{$option_ref->{"CODEG"}->{$coDEG}})."_"."co_DEG";
		`mkdir -p $co_dir` if ( !-d $co_dir);
		$co_dir = &AbsolutePath("dir",$co_dir); chdir($co_dir);
		# print `pwd`;
		my $venn_f_down = join(",",@Down_file);
		my $venn_f_up = join(",",@Up_file);
		my $codeg_name = join("-",@{$option_ref->{"CODEG"}->{$coDEG}});
		my $sigfilelist = join(",",@Sig_file);
		`perl $Bin/co_DEG.pl -i $sigfilelist > $codeg_name\_coDEG.log`;
		`find ./ -name "_*.txt" | perl -ne 'chomp;\$name = \$_; \$name=~s/.txt//;print "perl $Bin/public/exp_add_anno.pl -exp \$_ -anno $EG_TPM -o \$name\\_add_exp.txt \\n";' > addexp.sh `;
		`sh addexp.sh`;
		if ($annofile ne "") {
			`find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "perl $Bin/public/exp_add_anno.pl -exp \$_ -anno $annofile -annonum auto -o \$name & \\n";' > anno.sh `;
			`sh anno.sh`;
		}else{
			`find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "mv \$_ \$name & \\n";' > anno.sh `;
			`sh anno.sh`;
		}
		print "Rscript $Bin/plot/Venn.r -f $venn_f_up -n $codeg_name\_co_UP_venn";
		`Rscript $Bin/plot/Venn.r -f $venn_f_up -n $codeg_name\_co_UP_venn`;
		print "Rscript $Bin/plot/Venn.r -f $venn_f_down -n $codeg_name\_co_DOWN_venn";
		`Rscript $Bin/plot/Venn.r -f $venn_f_down -n $codeg_name\_co_DOWN_venn`;
	}
	`cd $codeg_dir && perl $Bin/public/pipeline_stat.pl -i ./ -p _co_DEG -m _coDEG.log -o coDEG_statics.xls`;
	chdir($outdir);
}

sub Di_DEG_analysis {    #&Select_co_DEG($method,$outdir,$file1,$file2,$i,$j,\%DEG_method)
	my ($option_ref, $outdir) = @_;
	chdir($outdir);
	`mkdir -p di_DEG` if ( !-d "di_DEG");
	my $dideg_dir = $outdir."/di_DEG";
	foreach my $diDEG (sort keys %{$option_ref->{"DIDEG"}}) {
		my @Sig_file = ();
		my @Up_file = ();
		my @Down_file = ();
		chdir($outdir);
		#print join(":",@{$option_ref->{"CODEG"}->{$coDEG}}),"\n";
		#print `pwd`;
		$outdir = &AbsolutePath("dir",$outdir);
		opendir(DH,$outdir) or die "$!\n";
		foreach my $element (readdir DH) {
			if (-d $element) {
				foreach my $group (@{$option_ref->{"DIDEG"}->{$diDEG}}) {
					if ($element =~ /$group/i ) {
						opendir(DIR,$element) or die "$!\n";
						print $outdir."/".$element,"\n";
						foreach my $file (readdir DIR) {
							next if $file !~ /^_/;
							if ($file =~ /_Sig_DEG.txt$/i) {
								push @Sig_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							}elsif ($file =~ /_Down_DEG.txt$/i) {
								push @Down_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							}elsif ($file =~ /_Up_DEG.txt$/i) {
								push @Up_file, $outdir."/".$element."/".$file;
								#print $outdir."/".$element."/".$file,"\n";
							} else {
								next;
							}
						}
					}
				}
			} else {
				next;
			}
		}
		close(DH);
		print join("\n",@Sig_file),"\n";
		chdir("di_DEG");
		# print `pwd`;
		my $di_dir = join("_and_",@{$option_ref->{"DIDEG"}->{$diDEG}})."_"."di_DEG";
		`mkdir -p $di_dir` if ( !-d $di_dir);
		$di_dir = &AbsolutePath("dir",$di_dir); chdir($di_dir);
		# print `pwd`;
		my $venn_f_down = join(",",@Down_file);
		my $venn_f_up = join(",",@Up_file);
		my $dideg_name = join("-",@{$option_ref->{"DIDEG"}->{$diDEG}});
		my $sigfilelist = join(",",@Sig_file);
		`perl $Bin/di_DEG.pl -i $sigfilelist >> $dideg_name\_diDEG.log`;
		`find ./ -name "_*.txt" | perl -ne 'chomp;\$name = \$_; \$name=~s/.txt//;print "perl $Bin/public/exp_add_anno.pl -exp \$_ -anno $EG_TPM -o \$name\\_add_exp.txt \\n";' > addexp.sh `;
		`sh addexp.sh`;
		if ($annofile ne "") {
			`find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "perl $Bin/public/exp_add_anno.pl -exp \$_ -anno $annofile -annonum auto -o \$name & \\n";' > anno.sh `;
			`sh anno.sh`;
		}else{
			`find ./ -name '*_add_exp.txt' | perl -ne 'chomp;\$name = \$_; \$name=~s/\\/_/\\//; \$name=~s/_add_exp.txt//;\$name .= ".txt"; print "mv \$_ \$name & \\n";' > anno.sh `;
			`sh anno.sh`;
		}
		`Rscript $Bin/plot/Venn.r -f $venn_f_up -n $dideg_name\_di_UP_venn`;
		`Rscript $Bin/plot/Venn.r -f $venn_f_down -n $dideg_name\_di_DOWN_venn`;
	}
	`cd $dideg_dir && cat *_di_DEG/*_diDEG.log|grep -v '#'|sed -e 's/:\\s/\\t/' > diDEG_statics.xls`;
	chdir($outdir);
}


sub select_index{
	my ($file,$sample) = @_;
	my $index = 0;
	open IN,$file;
	my $title = <IN>;
	close IN;
	chomp($title);
	my @line=split(/\t/,$title);
	for(my $i=0;$i<scalar(@line);$i++){
		if($line[$i] eq $sample){
			$index = $i;
			return $index;
		}
	}
	return -1;
}

sub AbsolutePath{		# Get the absolute path of the target directory or file
	my ($type,$input) = @_;
	my $return;
	if ($type eq "dir"){
		my $pwd = `pwd`;
		chomp $pwd;
		chdir($input);
		$return = `pwd`;
		chomp $return;
		chdir($pwd);
	} elsif($type eq 'file'){
		my $pwd = `pwd`;
		chomp $pwd;
		my $dir=dirname($input);
		my $file=basename($input);
		chdir($dir);
		$return = `pwd`;
		chomp $return;
		$return .="\/".$file;
		chdir($pwd);
	}
	return $return;
}



############Time_end#############
my $Time_End;
$Time_End = sub_format_datetime( localtime( time() ) );
print "\nEnd Time :[$Time_End]\n\n";

my $time_used = time() - $start_time;
my $h         = $time_used / 3600;
my $m         = $time_used % 3600 / 60;
my $s         = $time_used % 3600 % 60;
printf( "\nAll Time used : %d hours\, %d minutes\, %d seconds\n\n", $h, $m,
	$s );

sub sub_format_datetime {    #Time calculation subroutine
	my ( $sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst ) = @_;
	$wday = $yday = $isdst = 0;
	sprintf(
		"%4d-%02d-%02d %02d:%02d:%02d",
		$year + 1900,
		$mon + 1, $day, $hour, $min, $sec
	);
}