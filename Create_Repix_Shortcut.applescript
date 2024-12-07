tell application "Finder"
    set projectPath to "/path/to/repix/run_repix.sh" -- Replace with the actual path to your repix folder
    set desktopPath to (path to desktop folder) as text
    
    make new alias file at folder desktopPath to file projectPath
    set name of result to "Launch Repix"
end tell 