$ErrorActionPreference = "Stop"

$outDir = "C:\Users\user\Documents\Playground\OWCStats\temp_video\full"
$jobName = "OWCStats480"
$videoPath = Join-Path $outDir "week1_day1_full_480.mp4"
$logPath = Join-Path $outDir "watch_extract.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] $Message"
}

function Extract-Frame {
    param(
        [string]$Timestamp,
        [string]$OutputPath
    )

    & ffmpeg -y -ss $Timestamp -i $videoPath -frames:v 1 $OutputPath | Out-Null
    if (Test-Path $OutputPath) {
        Write-Log "Extracted frame: $OutputPath at $Timestamp"
    }
    else {
        Write-Log "Failed to extract frame: $OutputPath at $Timestamp"
    }
}

Write-Log "Watcher started."

while ($true) {
    $job = Get-BitsTransfer -Name $jobName -ErrorAction SilentlyContinue

    if (-not $job) {
        Write-Log "BITS job not found. Exiting watcher."
        break
    }

    Write-Log "BITS state=$($job.JobState) transferred=$($job.BytesTransferred) total=$($job.BytesTotal)"

    if ($job.JobState -eq "Transferred") {
        Complete-BitsTransfer -BitsJob $job
        Write-Log "BITS transfer completed and finalized."

        Extract-Frame -Timestamp "01:11:34" -OutputPath (Join-Path $outDir "m1g1_full_480.jpg")
        Extract-Frame -Timestamp "01:35:42" -OutputPath (Join-Path $outDir "m1g2_full_480.jpg")
        Extract-Frame -Timestamp "01:56:56" -OutputPath (Join-Path $outDir "m1g3_full_480.jpg")

        Write-Log "Watcher finished."
        break
    }

    if ($job.JobState -in @("Error", "TransientError", "Cancelled")) {
        Write-Log "BITS transfer ended with state: $($job.JobState)"
        break
    }

    Start-Sleep -Seconds 60
}
