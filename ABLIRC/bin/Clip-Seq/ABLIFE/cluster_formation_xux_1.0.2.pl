#!/usr/bin/perl -w
# 
# Copyright (c)   AB_Life 2011
# Writer:         xuxiong <xuxiong19880610@163.com>
# Program Date:   2011.
# Modifier:       xuxiong <xuxiong19880610@163.com>
# Last Modified:  2011.
my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programme，you must write the detailed time、discriptions、parameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"i=s","o=s","extend" );

if(!defined($opts{i}) || !defined($opts{o}) )
{
	print <<"	Usage End.";

	Description:This programme is used for ~
		
		Version: $ver

	Usage:perl $0

		-i           infile             must be given

		-o           outfile            must be given

		-extend      extend flank length(25)   option

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
###################################

my $in=$opts{i};	#infile
my $out=$opts{o};	#outfile
my $flank_len=defined $opts{extend} ? $opts{extend} : 25;		#merge the reads as cluster if distance is less $fland_len, not used!

my $read_count=0;
my $cluster_count=0;
my @cluster;
my @temp=();
my @pos=();

my %hash=();
my @array=();
#Chr1    2722    2743    SBS_0010:3:12:12298:8569#0/1,SBS_0010:3:120:9975:19413#0/1      2       +
#Chr1    2731    2753    SBS_0010:3:8:9926:2983#0/1,SBS_0010:3:50:14303:15212#0/1        2       +
#Chr1    4004    4025    SBS_0010:3:96:12875:18008#0/1,SBS_0010:3:100:14025:4558#0/1     2       -

my %peak=();
my %peak_count=();
my $tmp_start;
my $tmp_strand;
my $PeakS = 0;
my $PeakE = 0;
open (IN,"$in") || die "Can't open $in\n";			#open a file as reading
while (<IN>) {
	chomp;
	my @line = split(/\t/,$_);
	if (not exists $peak_count{$line[0]}{$line[-1]}) {
		$peak_count{$line[0]}{$line[-1]}=0;
		$PeakS = $line[1];
		$PeakE = $line[2];
		push @{$peak{$line[0]}{$line[-1]}->[$peak_count{$line[0]}{$line[-1]}]},[@line];
	} else {
		my $overlap = &overlap_indentify(\$PeakS,\$PeakE,$line[1],$line[2]);
		if ($overlap>0) {
			push @{$peak{$line[0]}{$line[-1]}->[$peak_count{$line[0]}{$line[-1]}]},[@line];
		} else {
			$PeakS = $line[1];
			$PeakE = $line[2];
			$peak_count{$line[0]}{$line[-1]}++;
			push @{$peak{$line[0]}{$line[-1]}->[$peak_count{$line[0]}{$line[-1]}]},[@line];
		}
	}
}
close(IN);

open (OUT,">$out") || die "Can't creat $out\n";		#open a file as writing
print OUT "#>id_in_chr\tchr\tstart\tend\ttags\tmaxheight\tsummit\tstrand\n";
print OUT "#tag info\n";
foreach my $chr (sort keys %peak) {
	foreach my $strand (sort keys %{$peak{$chr}}) {
		for (my $i=0;$i<=$#{$peak{$chr}{$strand}} ;$i++) {
			my $start = min( map { @{$_}[1] } @{$peak{$chr}{$strand}[$i]} );
			my $end = max( map { @{$_}[2] } @{$peak{$chr}{$strand}[$i]} );
			print OUT ">$chr\_$strand\_$i\t$chr\t$start\t$end\t",scalar(@{$peak{$chr}{$strand}->[$i]}),"\t",&max_cluster_height($peak{$chr}{$strand}->[$i],$start,$end),"\t$strand\n";
			for (my $j=0;$j<=$#{$peak{$chr}{$strand}->[$i]} ;$j++) {
				print OUT join("\t",@{$peak{$chr}{$strand}->[$i]->[$j]}),"\n";
			}
		}
	}
}
close(OUT);

sub overlap_indentify {
	my ($start1,$end1,$start2,$end2)=@_;
	if ($$end1 < $start2 || $$start1 > $end2) {
		return 0;
	} else {
		$$start1 = ($$start1 < $start2) ? $$start1 : $start2;
		$$end1 = ($$end1 > $end2) ? $$end1 : $end2;
		return 1;
	}
}

sub max_cluster_height{
	my ($array,$cluster_start,$cluster_end) =@_;
	my %hash=();
	my $max_height;
	my $max_count;
	for (my $i=0;$i<=$#{$array} ;$i++) {
		for (my $j=$array->[$i]->[1];$j<=$array->[$i]->[2] ;$j++) {
			$hash{$j}++;
		}
	}
	my @values=values %hash;
	&Max(\@values,\$max_height,\$max_count);
	return $max_height."\t".$max_count;
}

sub Max {
	my ($array,$max,$max_count)=@_;
	$$max=$array->[0];
	$$max_count=0;
	for (my $i=1;$i<= $#{$array} ;$i++) {
		if ($array->[$i]>$$max) {
			$$max = $array->[$i] ;
			$$max_count = $i;
		}
	}
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

