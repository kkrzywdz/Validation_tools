# PowerShell script to monitor memory usage and save to a file with a timestamp

$filename = "MemoryUsageLog_" + $(get-date -Format "HHMMss") + ".txt"
# Define the output file path
$outputFilePath = "C:\" + $filename

# Function to get memory usage by a specific process
function Get-ProcessMemoryUsage {
    param (
        [string]$processName
    )

    # Get all processes with the specified name
    $processes = Get-Process $processName -ErrorAction SilentlyContinue
    $memoryUsagesMB = @()

    # Loop through each process and calculate memory usage in MB
    foreach ($process in $processes) {
        $memoryUsageMB = [math]::Round($process.WorkingSet64 / 1024 / 1024, 2)
        $memoryUsagesMB += $memoryUsageMB
    }

    # Return the list of memory usages in MB
    return $memoryUsagesMB
}


# Write the header to the output file
"Timestamp, Total Memory Usage (bytes), System Memory Usage (bytes), BenchmarkApp Memory Usage (bytes)" | Out-File $outputFilePath

while ($true) {
    # Get the current timestamp
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # Get the total and free physical memory
    $memory = Get-WmiObject Win32_OperatingSystem
    $totalVisibleMemoryBytes = $memory.TotalVisibleMemorySize * 1024
    $freeMemoryBytes = $memory.FreePhysicalMemory * 1024
    $usedMemoryBytes = $totalVisibleMemoryBytes - $freeMemoryBytes

    # Get the system memory usage (kernel memory)
    $systemMemory = Get-WmiObject Win32_PerfRawData_PerfOS_Memory
    $systemMemoryBytes = ($systemMemory.PoolPagedBytes + $systemMemory.PoolNonpagedBytes)

    # Get the memory usage of the benchmarkapp process
    $benchmarkAppMemoryUsageBytes = (Get-ProcessMemoryUsage -processName "benchmark_app")

    # Create the output string
    $outputString = "$timestamp, $([math]::Round($usedMemoryBytes / 1024 /1024 /1024, 2)), GB , $([math]::Round($systemMemoryBytes/ 1024 /1024 /1024,2)) , GB, $benchmarkAppMemoryUsageBytes ,MB"

    # Output to console
    Write-Output $outputString

    # Append the output to the file
    $outputString | Out-File $outputFilePath -Append

    # Wait for 1 second
    Start-Sleep -Seconds 1
}
