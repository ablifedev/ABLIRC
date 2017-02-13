#!/usr/bin/perl -w

=head1 Example

    perl stastics.pl samplesheet rawstat cleanstat uniqtagstat
=cut

use strict;

my ( $rawdata, $uniqtag, $gc_dup, $q30 ) = @ARGV;
open IN1, "<$rawdata"    or die $!;
open OUT, ">statout.xls" or die $!;

print OUT
    "SampleName\trawReads\tcleanReads\tratioReads\trawBase\tcleanBase\tratioBase\tuniqtag\tQ20\tQ30\tGC\tDUP\n";




my (%rawdata, %cleandata, %rawbase, %cleanbase, %per, %perbase,
    %uniqtag, %gc,        %dup,     %q20,       %q30
);
while (<IN1>) {
    chomp;
    next if (/^samplename\s+/);
    next if (/^$/);
    my @line  = split(/\t/);
    my $sname = $line[0];

    $rawdata{ $line[0] }   = $line[1];
    $cleandata{ $line[0] } = $line[3];
    $rawbase{ $line[0] }   = $line[2];
    $cleanbase{ $line[0] } = $line[4];


    open IN4, "<$uniqtag" or die $!;
    while (<IN4>) {
        chomp;
        my @uniqt = split;
        if (/\/$sname\.fq/) {
            $uniqtag{$sname} = $uniqt[2];
        }
    }
    close(IN4);


    open IN5, "<$gc_dup" or die $!;
    while (<IN5>) {
        chomp;
        my @gd = split;
        if (/^$sname\s+/) {
            $gc{$sname}  = $gd[1];
            $dup{$sname} = $gd[2];
        }
    }
    close(IN5);


    open IN6, "<$q30" or die $!;
    while (<IN6>) {
        chomp;
        my @q = split;
        if (/\/$sname\.fq/) {
            $q20{$sname} = $q[1];
            $q30{$sname} = $q[2];
        }
    }
    close(IN6);

    $per{$sname}     = 0;
    $perbase{$sname} = 0;

    $per{$sname}
        = sprintf( "%3.2f%%", $cleandata{$sname} / $rawdata{$sname} * 100 )
        if $rawdata{$sname} > 0;
    $perbase{$sname}
        = sprintf( "%3.2f%%", $cleanbase{$sname} / $rawbase{$sname} * 100 )
        if $rawbase{$sname} > 0;
    my $raw = $rawbase{$sname};
    $rawbase{$sname} = sprintf( "%.3f", $raw / 1000000000 ) . "G";

    # if ($rawbase{$sname} eq "0.00G"){
    #   $rawbase{$sname}=sprintf("%.2f",$raw/1000000)."M";
    #   if ($rawbase{$sname} eq "0.00M"){
    #       $rawbase{$sname}=$raw."bp";
    #   }
    # }

    my $clean = $cleanbase{$sname};
    $cleanbase{$sname} = sprintf( "%.3f", $clean / 1000000000 ) . "G";

    # if ($cleanbase{$sname} eq "0.00G"){
    #   $cleanbase{$sname}=sprintf("%.2f",$clean/1000000)."M";
    #   if ($cleanbase{$sname} eq "0.00M"){
    #       $cleanbase{$sname}=$clean."bp";
    #   }
    # }

    print OUT
        "$sname\t$rawdata{$sname}\t$cleandata{$sname}\t$per{$sname}\t$rawbase{$sname}\t$cleanbase{$sname}\t$perbase{$sname}\t$uniqtag{$sname}\t$q20{$sname}\t$q30{$sname}\t$gc{$sname}\%\t$dup{$sname}\%\n";

}

close IN1;
close OUT;
