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
use threads;  
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

#Before writing your programmeyou must write the detailed timediscriptionsparameter and it's explanation,Meanwhile,annotation your programme in English if possible.

my %opts;
GetOptions(\%opts,"gene_peak=s","times=s","outdir=s");

if(!defined($opts{gene_peak}) || !defined($opts{times}) || !defined($opts{outdir})  )
{
	print <<"	Usage End.";

	Description:This programme is used for 
		
		Version: $ver

	Usage:perl $0

		-gene_peak           infile          must be given

		-times               infile          must be given

		-outdir              outfile         must be given

	Usage End.

	exit;
}

###############Time_start##########
my $Time_Start;
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n";
my $BEGIN_TIME=time();
###################################

my $gene_peak=$opts{gene_peak};
my $times=$opts{times};
my $max_thread = 50; 
my $current_thread = 0;
my @thread_array=();

my $current_dir = `pwd`;chomp($current_dir);
my $outdir = defined $opts{outdir} ? $opts{outdir} : "./";
`mkdir -p $outdir` if (!-d $outdir) ;
$outdir = "$current_dir/$outdir" if ($outdir!~/^\/|\~/) ;
my @array=();
open (PVALUE,">$outdir/p_value") || die $!;
open (GENE_PEAK,"<$gene_peak") || die $!;
$/="Gene:";
my $gene_count=0;
while (<GENE_PEAK>) {
	chomp;
	next if (/^$/) ;
	my @line=split(/\n/,$_);
	my @gene_pos=split("\t",shift(@line));
	pop(@line);
	my @tag_len=();
	foreach my $temp_line (@line) {
		my @temp_tag=split(/\t/,$temp_line);
		if ($temp_line!~/^>/) {
			push @tag_len,(abs($temp_tag[2]-$temp_tag[1])+1);
		}
		elsif ($temp_line=~/^>/){########### locate the gene position again
			if ($temp_tag[2]<$gene_pos[1]) {
				$gene_pos[1]=$temp_tag[2];
			}
			elsif($temp_tag[3]>$gene_pos[2]){
				$gene_pos[2]=$temp_tag[3];
			}
		}
	}
	$gene_count++;
	if ($gene_count%100 ==0) {
		print time()-$BEGIN_TIME,"\n";
	}

	#if( $current_thread >= $max_thread ) { 
		#foreach my $thread( @thread_array ) { 
			#$thread -> join( ); 
		#} 
		#$current_thread = 0; 
	#}
	#$thread_array[$current_thread] = threads -> new( \&in_silico_random,$gene_pos[3],$times,$gene_pos[1],$gene_pos[2],\@tag_len,\*PVALUE ); 
	#$current_thread ++; 

	&in_silico_random($gene_pos[3],$times,$gene_pos[1],$gene_pos[2],\@tag_len,\*PVALUE);

}
close(GENE_PEAK);
close(PVALUE);




sub read_file{
	my ($infile_handle,$outfile_handle,$max_gene);
	my $gene_count=0;
	while (<$infile_handle>) {
		chomp;
		next if (/^$/) ;
		my @line=split(/\n/,$_);
		my @gene_pos=split("\t",shift(@line));
		pop(@line);
		my @tag_len=();
		foreach my $temp_line (@line) {
			my @temp_tag=split(/\t/,$temp_line);
			if ($temp_line!~/^>/) {
				push @tag_len,(abs($temp_tag[2]-$temp_tag[1])+1);
			}
			elsif ($temp_line=~/^>/){########### locate the gene position again
				if ($temp_tag[2]<$gene_pos[1]) {
					$gene_pos[1]=$temp_tag[2];
				}
				elsif($temp_tag[3]>$gene_pos[2]){
					$gene_pos[2]=$temp_tag[3];
				}
			}
		}
		&in_silico_random($gene_pos[3],$times,$gene_pos[1],$gene_pos[2],\@tag_len,$outfile_handle);
		$gene_count++;
		return if ($gene_count>=1000) ;
	}
}


sub in_silico_random{
	my ($GeneID,$Times,$Gene_start,$Gene_end,$array_len,$file_handle)=@_;
	my %MAX_HEIGHT=();
	for (0..$Times-1) {
		my $current_max_height=&random_peak_max_height($Gene_start,$Gene_end,$array_len);
		$MAX_HEIGHT{$current_max_height}++;
	}
	print $file_handle "#########################\n";
	print $file_handle "Gene:",$GeneID,"\n";
	my %cumulative_p_value=();
	my @keys =sort {$a <=> $b} keys %MAX_HEIGHT;
	my $i=0;
	foreach my $key_MAX_HEIGHT (@keys ) {
		print $file_handle $key_MAX_HEIGHT,"\t",$MAX_HEIGHT{$key_MAX_HEIGHT},"\t",sprintf("%2.4f",$MAX_HEIGHT{$key_MAX_HEIGHT}/$times),"\t";
		$cumulative_p_value{$key_MAX_HEIGHT}=sprintf("%2.4f",sum(map {$MAX_HEIGHT{$_}/$Times} @keys[$i..$#keys]));
		$i++;
		print $file_handle $cumulative_p_value{$key_MAX_HEIGHT},"\n";
	}
}

sub random_peak_max_height{ #(\$gene_start, \$gene_end, \@random_tag_length)
	my ($gene_start,$gene_end,$ref_array)=@_;
	my $gene_length = abs($gene_start-$gene_end)+1;
	my %pos = ();
	for (my $i=0; $i<=$#{$ref_array}; $i++) {
		my $random_start = $gene_start+int(rand($gene_length-$ref_array->[$i]));
		my $random_end = $random_start+$ref_array->[$i]-1;
		map {$pos{$_}++} ($random_start..$random_end);
	}
	return max(values(%pos));
}

##############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n";

###############Sub_format_datetime
sub sub_format_datetime {#Time calculation subroutine
    my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
	$wday = $yday = $isdst = 0;
    sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour, $min, $sec);
}
