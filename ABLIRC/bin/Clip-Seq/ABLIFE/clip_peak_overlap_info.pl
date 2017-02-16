#!/usr/bin/perl -w
use strict;
use Getopt::Long;

=head1 Description

Program: clip_peak_overlap_info

Author: Ablife

Version: 1.0

使用bedtools cluster将ablife,piranha,cims三种方法得到的peak进行cluster后，需对应回源文件，补充完整的peak信息，同时加入cluster信息

=head1 Usage

perl nonoverlap_CIMS.pl [options]

    -a   ablife addanno peak file, required

    -b   piranha addanno peak file, required

    -c   cims addanno peak file, required

    -i   cluster info, required

    -o   result file, default is "allpeaks_cluster_type.bed"

    -h      output help information

=cut

die `pod2text $0` if (@ARGV < 4);

my ($ablife,$piranha,$cims,$info,$out,$help);
GetOptions(
			"a:s"=>\$ablife,
			"b:s"=>\$piranha,
			"c:s"=>\$cims,
            "i:s"=>\$info,
			"o:s"=>\$out,
			"h"=>\$help
			);

die `pod2text $0` if ($help);

$out||="allpeaks_cluster_type.bed";

print "Command:\n  perl $0 -a $ablife -b $piranha -c $cims -i $info -o $out\n\n";

my (@line,%hash) ;

open A,"$ablife";
while (<A>){
    chomp;
    next if(/^#/);
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash{$key}= $_;
}
close A;

open A,"$piranha";
while (<A>){
    chomp;
    next if(/^#/);
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash{$key}= $_;
}
close A;

open A,"$cims";
while (<A>){
    chomp;
    next if(/^#/);
    @line=split /\t/,$_;
    my $key = join("\t",@line[0..5]);
    $hash{$key}= $_;
}
close A;

open OUT, ">$out";

open INFO,"$info";
while (<INFO>){
    chomp;
    @line=split /\t/,$_;
    my $type="";
    if($line[3] eq "X"){
        $type = "piranha";
    }elsif($line[3] =~/k=/){
        $type = "cims";
    }else{
        $type = "ablife";
    }
    my $key = join("\t",@line[0..5]);
    print OUT $hash{$key},"\t",$line[6],"\t",$type,"\n";
}
close INFO;
close OUT;

#################################
########## Sub Routine ##########
#################################
