PARAM([string]$path, [string]$version, [string]$branch)

$user = "svc-ArchiveMgrBuild@prod.quest.corp";
$pwd = "Password1";

$uString = [string]::Format("{0}:{1}", $user, $pwd);

$installerSrc = [string]::Format("{0}\\ArchiveManagerInstaller.msi", $path);
$installerDes = [string]::Format("https://artifactory.labs.quest.com/qam-build/builds/{0}/release/AM-{1}/ArchiveManagerInstaller.msi", $branch, $version);

$autoRunSrc = [string]::Format("{0}\\ArchiveManagerAutoRun.exe", $path);
$autoRunDes = [string]::Format("https://artifactory.labs.quest.com/qam-build/builds/{0}/release/AM-{1}/ArchiveManagerAutoRun.exe", $branch, $version);

Write-Host "Copying installer from $installerSrc to artifactory: $installerDes.";
cmd /c curl -u $uString -T $installerSrc $installerDes;

Write-Host "Copying installer from $autoRunSrc to artifactory: $autoRunDes.";
cmd /c curl -u $uString -T $autoRunSrc $autoRunDes;