use strict;
use File::Copy;


system('OCI_Auditing_Tool.exe "mytenancy12 mytenancy09" "policies events networks" sendMail');


my @allFiles = glob(".\\results\\*.*");
my @xlsFiles = glob(".\\results\\*.xlsx");


### Moving files to Cloud drives, which will get synced and 
### will be available for all users.

for my $f (@xlsFiles){
	move($f, 'C:\Users\opc\Oracle Content - Accounts\OCI Auditing [Shared]\mytenancy-Daily Reports\\');
}
for my $f (@allFiles){
	move($f, ".\\results\\logs\\");
}

