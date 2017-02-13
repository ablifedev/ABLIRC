my @rows = ();
my @transposed = ();

open F1,$ARGV[0];
while(<F1>) {
    chomp;
    push @rows, [split  /\t/ ];
}
#print @rows;

for my $row (@rows) {
  for my $column (0 .. $#{$row}) {
    push(@{$transposed[$column]}, $row->[$column]);
  }
}

for my $new_row (@transposed) {
  for my $new_col (@{$new_row}) {
      print $new_col, "\t";
  }
  print "\n";
}