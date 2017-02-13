echo -ne "#"
cat $1 | perl -ne 'chomp;@line=split(/\t/);print $line[1],"\t",$line[2],"\t",$line[3],"\t",$line[0],"\t",$line[5],"\t",$line[4],"\n";'