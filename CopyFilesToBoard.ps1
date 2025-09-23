$sourceDir = ".\source"  # Replace with your source directory
$destDir = "D:"  # Replace with your destination directory
$excludedFolders = @("lib")  # List of folder names to exclude

$sourceDirFullPath = Resolve-Path -Path $sourceDir

# Get all files in the source directory and its subdirectories, excluding specified folders
$files = Get-ChildItem -Path $sourceDir -File -Recurse | Where-Object {
    $exclude = $false
    foreach ($folder in $excludedFolders) {
        if ($_.FullName -like "*\$folder\*") {
            $exclude = $true
            break
        }
    }
    -not $exclude
}

foreach ($file in $files) {
    # Create the destination path by replacing the source directory path with the destination directory path
    $relativePath = $file.FullName.Substring($sourceDirFullPath.Path.Length + 1)  # Get the relative path
    $destFile = Join-Path -Path $destDir -ChildPath $relativePath

    # Ensure the destination directory exists
    $destDirectory = Split-Path -Path $destFile -Parent
    if (-not (Test-Path -Path $destDirectory)) {
        New-Item -ItemType Directory -Path $destDirectory -Force
    }

    # Check if the destination file exists
    if (Test-Path -Path $destFile) {
        # Compare last write times
        $sourceLastWriteTime = $file.LastWriteTime
        $destLastWriteTime = (Get-Item -Path $destFile).LastWriteTime

        # Only copy if the source file is newer
        if ($sourceLastWriteTime -gt $destLastWriteTime) {
            Copy-Item -Path $file.FullName -Destination $destFile -Force
            Write-Host "Copied: $($file.Name)"
        } else {
            Write-Host "Skipped: $($file.Name)"
        }
    } else {
        # If the destination file does not exist, copy it
        Copy-Item -Path $file.FullName -Destination $destFile
        Write-Host "Copied: $($file.Name)"
    }
}