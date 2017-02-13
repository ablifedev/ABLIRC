#!/usr/bin/perl -w
my $ver = "1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use FileHandle;

my %opts;
GetOptions( \%opts, "genome=s","window=s", "o=s", "h" );

if ( !defined( $opts{genome} ) || defined( $opts{h} ) )
{
	print <<"	Usage End.";

		Version:$ver

	Usage:perl $0

		-genome     genome                             must be given;
		
		-window     simulate gene window               option(default is 1000);

		-o          out file                           must be given;

	Usage End.

	exit;
}

#############Time_start#############
my $start_time = time();

my $Time_Start;
$Time_Start = sub_format_datetime( localtime( time() ) );
print "\nStart Time :[$Time_Start]\n\n";
####################################

my $genome_file  = $opts{genome};
my $window  = $opts{window} || 1000;
my $out_file = $opts{o};

open OUT, ">$out_file" || die;
# chr1    HAVANA  gene    11869   14409   .       +       .       ID=ENSG00000223972.5;
# chr1    HAVANA  transcript      11869   14409   .       +       .       ID=ENST00000456328.2;Parent=ENSG00000223972.5;
# chr1    HAVANA  exon    11869   12227   .       +       .       ID=exon:ENST00000456328.2:1;Parent=ENST00000456328.2;

`getChrLength.pl $genome_file chrlen` if (!-f "chrlen");

my %chr = ();
open IN,"chrlen";
while(<IN>){
	chomp;
	my @line=split(/\t/);
	$chr{$line[0]}=$line[1];
}
close IN;

for my $Chr (sort keys %chr){
	for (my $s = 1;$s<$chr{$Chr};$s=$s+$window){
		my $e=$s+$window-1;
		$e = $chr{$Chr} if $e > $chr{$Chr};
		my $geneid = $Chr."_".$s."_".$e;
		my $isoformid = $geneid.".1";
		my $exonid = "exon:".$isoformid.":1";
		print OUT "$Chr\tSimulate\tgene\t$s\t$e\t\.\t+\t\.\tID=$geneid;\n";
		print OUT "$Chr\tSimulate\ttranscript\t$s\t$e\t\.\t+\t\.\tID=$isoformid;Parent=$geneid;\n";
		print OUT "$Chr\tSimulate\texon\t$s\t$e\t\.\t+\t\.\tID=$exonid;Parent=$isoformid;\n";
	}
}

close OUT;

############Time_end#############
my $Time_End;
$Time_End = sub_format_datetime( localtime( time() ) );
print "\nEnd Time :[$Time_End]\n\n";

my $time_used = time() - $start_time;
my $h = $time_used/3600;
my $m = $time_used%3600/60;
my $s = $time_used%3600%60;
printf("\nAll Time used : %d hours\, %d minutes\, %d seconds\n\n",$h,$m,$s);


#######Sub_format_datetime#######
sub sub_format_datetime {    #Time calculation subroutine
	my ( $sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst ) = @_;
	$wday = $yday = $isdst = 0;
	sprintf(
		"%4d-%02d-%02d %02d:%02d:%02d",
		$year + 1900,
		$mon + 1, $day, $hour, $min, $sec
	);
}