#!/usr/bin/perl -w

my $ver="1.0.0";

use strict;
use Getopt::Long;
use Data::Dumper;
use FindBin qw($Bin $Script);
use File::Basename qw(basename dirname);
use List::Util qw(first max maxstr min minstr reduce shuffle sum);

my %opts;
GetOptions(\%opts,"i=s","o=s","p=s","max_len=s","min_match=s");

if(!defined($opts{i}) || !defined($opts{o}))
{
		print <<"		Usage End.";

		Description:This programme is used for counting length of the sequecnces.

		Example:perl /users/xux/work/perl/CLIP-seq/stat_read_length.pl -i /data2/arabidopsis/CLIP-seq/CLIP_0810 -o oooo -p _0822

			Version:$ver

		Usage:perl $0

			-i          indir              must be given 

			-o          outfile            must be given
			
			-p          postfix            option

			-max_len    max_length         option

			-min_match  minimum alignment  option

		Usage End.

		exit;
}

###############Time_start##########
my $Time_Start; 
$Time_Start = sub_format_datetime(localtime(time()));
print "\nStart Time :[$Time_Start]\n\n"; 
#################################### 

my $current_dir=`pwd`;chomp($current_dir);
my $indir = $opts{i};
my $out=$opts{o};
my $postfix=defined $opts{p} ? $opts{p} : "_clipper.fq";
my $max_length=defined $opts{max_len} ? $opts{max_len} : 32;
my $min_match=defined $opts{min_match} ? $opts{min_match} : 3;

chdir($indir);
my @raw_trim_tag=glob "*$postfix";

my %total=();
my %hash=();
for (my $i=0;$i<@raw_trim_tag ;$i++) {
	$raw_trim_tag[$i]=~/(\S+)_clipper\.fq/;
	my $S=$1;
	$total{$S}=&load_fq($raw_trim_tag[$i],\%{$hash{$S}});
	print ref($hash{$S}),"\t",$S,"\t",$total{$S},"\n";
}

my @key=();
my @value=();
my @percent=();

foreach my $key_S (sort keys %hash) {
	push @key,keys %{$hash{$key_S}};
	push @value,values %{$hash{$key_S}};
	push @percent,map {$_/$total{$key_S}*100} values(%{$hash{$key_S}});
}

print scalar(@key),"\t",scalar(@value),"\t",scalar(@percent),"\n";

chdir($current_dir);
open (OUT,">$out.percent.list") || die "Can't creat $out\n";     #open a file as writing
my $X_end=max(@key)+1;
my $X_Cut=max(@key)-$min_match;
my $X_start=min(@key);
my $X_step=int(($X_end - $X_start)/5);
my $Y_end=int(max(@value)*5/4000);
my $Y_step=int($Y_end/5);
my $RY_End= max(@percent)*5/4;
my $RY_Step=int($RY_End/5);
print OUT <<"	Usage End.";
Type:Rect
PointSize:2
Width:600
Height:400
WholeScale:0.9
Fontsize:46
TextScale:0.8
XStart:$X_start
XStep:$X_step
XEnd:$X_end
#XCut:$X_end
YStart:0
YStep:$Y_step
YEnd:$Y_end
RYStart:0
RYStep:$RY_Step
RYEnd:$RY_End
MarkNoBorder:0
#XScaleRoate:75
XUnit:1
UnitPer:0.3
OffsetPer:0.33
MovePer:0.15
XMove:0
XScalePos:0
MarkPos:l
MarkScale:0.5
Note:Distribution of Reads length
X:Reads length
Y:Number of Reads(Kbp)
RY:Percentage of Reads(%)
FontFamily:ArialNarrow-Bold
#XScale:
#6
#12
#18
#24
#
#29+
#:End

	Usage End.

my @color=("#FF0000","#00FF00","#0000FF","#FF00FF","#00FFFF");

foreach my $key_S (sort keys %hash) {
	my $Color=shift(@color);
	print $Color,"\n";
	print OUT "\nColor:$Color\nMark:$key_S\n";
	foreach my $key_len (sort {$a<=>$b} keys %{$hash{$key_S}}) {
		#print $key_len,"\n";
		my $current_percent = sprintf("%3.3f",$hash{$key_S}{$key_len}/$total{$key_S}*100);
		print OUT "$key_len:$current_percent\n";
		print OUT "$key_len:",$hash{$key_S}{$key_len}/1000,"\n";
	}
}
close(OUT);

`cd $current_dir && perl /public/software/svg/distributing_svg.pl $out.percent.list $out.svg `;
`/public/software/svg/svg2xxx_release/svg2xxx $out.svg && rm $out.svg`;


sub load_fq{
	my ($infile,$hash_ref)=@_;
	my $total=0;
	open (IN,$infile) or die $!;
	while (<IN>) {
		chomp;
		my $seq=<IN>;
		chomp $seq;
		$total++;
		my $length=length($seq);
#		$length-=$min_match if ($length == $max_length) ;
		$hash_ref->{$length}++;
		my $third_line=<IN>;
		my $Q=<IN>;
	}
	close IN;
	return $total;
}

###############Time_end###########
my $Time_End;
$Time_End = sub_format_datetime(localtime(time()));
print "\nEnd Time :[$Time_End]\n\n"; 
################Sub_format_datetime#
sub sub_format_datetime {#Time calculation subroutine
		my($sec, $min, $hour, $day, $mon, $year, $wday, $yday, $isdst) = @_;
		$wday = $yday = $isdst = 0;
		sprintf("%4d-%02d-%02d %02d:%02d:%02d", $year+1900, $mon+1, $day, $hour,$min, $sec); 
}
