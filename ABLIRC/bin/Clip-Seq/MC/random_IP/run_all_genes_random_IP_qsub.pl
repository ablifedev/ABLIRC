#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.06.28
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.06.28
my $ver="1.0.0";

use strict;
use warnings;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"gene_peak=s","times=s","outdir=s","f=s","maxprc=s" );

if(!defined($opts{gene_peak}) || !defined($opts{times}) || !defined($opts{outdir})  )
{
	print <<"	Usage End.";

	Description:This programme is used for 
		
		Version: $ver

	Usage:perl $0

		-gene_peak           infile          must be given

		-times               infile          must be given

		-outdir              outfile         must be given

		-maxprc              max_process(200)       option

		-f                   fdr 阈值        default is 0.001

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $gene_peak=$opts{gene_peak};
# my $trans_len=$opts{trans_len};
my $times=defined $opts{times} ? $opts{times} : 500 ; # default simulation is 500
my $maxprc=defined $opts{maxprc} ? $opts{maxprc} : 200 ;
my $fdr=defined $opts{f} ? $opts{f} : 0.001 ;

my $current_dir = `pwd`;chomp($current_dir);
my $outdir = defined $opts{outdir} ? $opts{outdir} : "./";
`rm -rf $outdir/*`;
`mkdir -p $outdir` if (!-d $outdir) ;
$outdir = "$current_dir/$outdir" if ($outdir!~/^\/|\~/) ;
#print $outdir,"\n";

# my %gene=();

# my %tlen = ();

# open(TRANLEN,"$trans_len") || die "can't find $trans_len";
# while(<TRANLEN>){
# 	chomp;
# 	next if(/^#/);
# 	print $_,"\n";
# 	my @line = split(/\t/);
# 	$tlen{$line[0]} = $line[1];
# }
# close TRANLEN;

my $shell=$outdir."/rand.sh";
open (SH,">$shell") || die "Can't creat $shell\n";		#open a file as writing
open (GENE_PEAK,"<$gene_peak") || die "Can't open $gene_peak\n";	#open a file as reading
$/="Gene:";
my $gene_count=0;
while (<GENE_PEAK>) {
	chomp;
	next if (/^\#+/) ;
	my @line=split(/\n/,$_);
	my @gene_pos=split("\t",shift(@line));
	pop(@line);
	my @tag_len=();
	foreach my $temp_line (@line) {
		my @temp_tag=split(/\t/,$temp_line);
		if ($temp_line!~/^>/) {
			push @tag_len,(abs($temp_tag[2]-$temp_tag[1])+1);
		}
		# elsif ($temp_line=~/^>/){		########### locate the gene position again
		# 	if ($temp_tag[2]<$gene_pos[1]) {
		# 		$gene_pos[1]=$temp_tag[2];
		# 	}
		# 	elsif($temp_tag[3]>$gene_pos[2]){
		# 		$gene_pos[2]=$temp_tag[3];
		# 	}
		# }
	}
	next if $gene_pos[3] eq "geneid";
	$gene_count++;
	# print $gene_pos[3],"\n";
	my $tranlen = $gene_pos[2] - $gene_pos[1] + 1;
	my $tlen = join(",",@tag_len);
	next if $tlen!~/^\d+/;
	print SH "cd $outdir && python2.7 $Bin/random_IP.py -g $gene_pos[3] -t $times -l $tranlen -r $tlen -o p_value_$gene_count -f $fdr && ";
	if($gene_count%100==0){
		print SH "\n";
	}
}
print SH "\n";
close(GENE_PEAK);
close(SH);

`perl /public/bin/qsub-sge.pl --queue new.q --resource vf=5.0G --maxproc $maxprc $shell`;
`rm -rf $outdir/p_value && ls $outdir/p_value_* | perl -ne 'chomp;system("cat \$_ >> $outdir/p_value");system("rm -rf \$_");'`;
#`rm $outdir/p_value_*`;
`cat $outdir/p_value | grep "FDR" > $outdir/fdr_threshold.txt`;

###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n";

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}
