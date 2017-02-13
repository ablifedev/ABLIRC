#!/usr/bin/perl -w
use strict;
use Getopt::Long;

=head1 Description

Program: nonoverlap_CIMS.pl

Author: Ablife

Version: 1.0

This script is used to pick up exp nonoverlap CIMS mutation position with ctrl

=head1 Usage

perl nonoverlap_CIMS.pl [options]

    -e   exp CIMS mutation file, required

    -c   ctrl CIMS mutation file, required

    -w   extend width from mutation position, default 20

    -o   result file, default is "nonoverlap_CIMS_result.txt"

    -h      output help information

=cut

die `pod2text $0` if (@ARGV < 3);

my ($exp,$ctrl,$wide,$out,$help);
GetOptions(
			"e:s"=>\$exp,
			"c:s"=>\$ctrl,
			"w:s"=>\$wide,
			"o:s"=>\$out,
			"h"=>\$help
			);

die `pod2text $0` if ($help);
if (! -f $exp) {
    print "\n[Error] $exp does not exist.\n\n";
    die `pod2text $0`;
}
if (! -f $ctrl) {
    print "\n[Error] $ctrl does not exist.\n\n";
    die `pod2text $0`;
}
$wide||=20;
if ($wide < 0) {
    print "\n[Warning] Set minimum length of wide is negative, program will use 20 instead.\n\n";
    $wide = 20;
}
$out||="nonoverlap_CIMS_result.txt";

print "Command:\n  perl $0 -e $exp -c $ctrl -w $wide -o $out\n\n";

my (@line,$name,$i,$id,%exist,$n,%seq,%val) ;
open CTRL,"$ctrl";
while (<CTRL>){
    chomp;
    @line=split /\t/,$_;
    $name="$line[0]"."_"."$line[5]";
    for ($i=$line[1]-$wide;$i<=$line[2]+$wide;$i++){
        $id="$name"."_"."$i";
        $exist{$id}=1;
    }
}

open EXP,"$exp";
while (<EXP>){
    chomp;
    $n=$_;
    $val{$n}=1;
    @line=split /\t/,$_;
    $name="$line[0]"."_"."$line[5]";
    for ($i=$line[1]-$wide;$i<=$line[2]+$wide;$i++){
        $id="$name"."_"."$i";
        if (defined $exist{$id}){
            $val{$n}=0;
            last;
        }
    }
}

open OUT, ">$out";
print OUT "#chrom\tchromStart\tchromEnd\tname\tscore\tstrand\ttagNumber(k)\tmutationFreq(m)\tFDR\tcount(>=m,k)\tmutationType\n";
my @keys=keys %val;
foreach (@keys){
    if ($val{$_}==1){
        print OUT "$_\n";
    }
}
close OUT;

#################################
########## Sub Routine ##########
#################################
