#!/usr/bin/perl -w
#
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.06.28
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.06.28
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"gene_peak=s","usesge=s","queue=s","trans_len=s","times=s","outdir=s","cpu=s" );

if(!defined($opts{gene_peak}) || !defined($opts{times}) || !defined($opts{outdir})  )
{
	print <<"	Usage End.";

	Description:This programme is used for

		Version: $ver

	Usage:perl $0

		-gene_peak           infile          must be given

		-trans_len           infile          must be given

		-times               infile          must be given

		-outdir              outfile         must be given

		-cpu              max_process(8)       option

		-usesge              use sge(yes)          option(yes/no)

		-queue              sge queue name(all.q)          option

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $gene_peak=$opts{gene_peak};
my $trans_len=$opts{trans_len};
my $times=defined $opts{times} ? $opts{times} : 500 ; # default simulation is 500
my $cpu=defined $opts{cpu} ? $opts{cpu} : 8 ;
my $usesge=defined $opts{usesge} ? $opts{usesge} : "yes" ;
my $queue=defined $opts{queue} ? $opts{queue} : "all.q" ;

my $current_dir = `pwd`;chomp($current_dir);
my $outdir = defined $opts{outdir} ? $opts{outdir} : "./";
`rm -rf $outdir/p_value_*`;
`mkdir -p $outdir` if (!-d $outdir) ;
$outdir = "$current_dir/$outdir" if ($outdir!~/^\/|\~/) ;
#print $outdir,"\n";

my %gene=();

my %tlen = ();

open(TRANLEN,"$trans_len") || die "can't find $trans_len";
while(<TRANLEN>){
	chomp;
	next if(/^#/);
	# print $_,"\n";
	my @line = split(/\t/);
	$tlen{$line[0]} = $line[1];
}
close TRANLEN;

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
		elsif ($temp_line=~/^>/){		########### locate the gene position again
			if ($temp_tag[2]<$gene_pos[1]) {
				$gene_pos[1]=$temp_tag[2];
			}
			elsif($temp_tag[3]>$gene_pos[2]){
				$gene_pos[2]=$temp_tag[3];
			}
		}
	}
	$gene_count++;
	# print $gene_pos[3],"\n";
	my $tranlen = $tlen{$gene_pos[3]};
	print SH "cd $outdir && perl $Bin/random_IP.pl $gene_pos[3] $times $tranlen @tag_len > p_value_$gene_count && ";
	if($gene_count % 40==0){
		print SH "\n";
	}
}
print SH "\n";
close(GENE_PEAK);
close(SH);

`perl $Bin/../../../public/qsub-sge.pl --usesge $usesge --queue $queue --maxproc $cpu $shell`;
for (my $i=1;$i<=$gene_count ;$i++) {
	`cat $outdir/p_value_$i >>$outdir/p_value`;
	`rm $outdir/p_value_$i`;
}

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
