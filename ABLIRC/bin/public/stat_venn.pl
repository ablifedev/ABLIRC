#!/usr/bin/perl
# @Author: anchen
# @Date:   2015-08-13 16:49:56
# @Last Modified by:   anchen
# @Last Modified time: 2015-08-14 15:15:14
use strict;
use Getopt::Long;
use FindBin qw($Bin $Script);
my @bin=split(/\//,$Bin);
my $len=scalar(@bin);
my $Bin=join('/',@bin[0..$len-2]);
my (%hash,%hash2,$key,@hash,$hash,@filename,$len,$i,$filename,$out,$help,$out,$value);
my (@lablename,$lablename);
GetOptions(
            "f:s"=>\$filename,
            "l:s"=>\$lablename,
            );
@filename=split /,/,$filename;
@lablename=split /,/,$lablename;

$len=@filename;

for($i=0;$i<$len;$i=$i+1){

    open (AA,"$filename[$i]");
    while (<AA>){
        chomp;
        my @line=split(/\t/);
        if (not defined($hash{$line[0]})){
            $hash{$line[0]}.="$lablename[$i]";
        }else{
            $hash{$line[0]}.="_olp_$lablename[$i]";
        }
        
    }
    close AA;
}
while(($key,$value)=each(%hash)){
    if (exists $hash{"$value"}){

        $hash2{"$value"}.="$key,";

    }
    else{
        $hash2{"$value"}.="$key,";

    }
}

`mkdir -p venn`;
while(($key,$value)=each(%hash2)){
    @hash=split /,/,$hash2{"$key"};
    $hash=@hash;
    $out=$key;
    $key=~s/_olp_/ olp /g;
    print "$key:$hash\n";
    open OUT, ">venn/$out.txt";
    foreach $hash(@hash){
        print OUT "$hash\n";
    }

}


`Rscript $Bin/plot/Venn_notitle.r -f $filename -d $lablename`;



#foreach $a(@a){
    #print "$a\n";
 #       }
#}
#$a=$hash2{"1_c"};
#print "$a\n";
#$len2=keys(%hash2);
#print $len2;




