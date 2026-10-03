; <COMPILER: v1.1.37.02>
#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
UpdaterVersion := "1.2"
UpdaterLog := A_ScriptDir . "\update_replace.log"
FileAppend, `n==== %A_Now% updater run ====`n, %UpdaterLog%
DefaultFileID := "12BguvI-s4tLE6_rRfB9208TSJuKZMzRT"
DriveLink := A_Args[1]
argCount := A_Args.Length()
FileAppend, [DEBUG] argCount = %argCount%`n, %UpdaterLog%
FileAppend, [DEBUG] Link raw: %DriveLink%`n, %UpdaterLog%
SourceHost := "drive"
FileID := ""
If (DriveLink != "" && InStr(DriveLink, "pixeldrain.com")) {
SourceHost := "pixeldrain"
FileID := RegExReplace(DriveLink, ".*/u/([a-zA-Z0-9_-]+)[/&?]?.*", "$1")
FileAppend, [DEBUG] Pixeldrain ID after regex: %FileID%`n, %UpdaterLog%
If (FileID = DriveLink || StrLen(FileID) < 5) {
FileAppend, [DEBUG] Pixeldrain regex failed`n, %UpdaterLog%
FileID := ""
}
} Else If (DriveLink != "" && InStr(DriveLink, "drive.google.com")) {
FileID := RegExReplace(DriveLink, ".*[/=]([a-zA-Z0-9_-]{25,})[/&?]?.*", "$1")
FileAppend, [DEBUG] Drive FileID after regex: %FileID%`n, %UpdaterLog%
If (FileID = DriveLink || StrLen(FileID) < 25)
FileID := ""
}
If (FileID = "") {
SourceHost := "drive"
FileID := DefaultFileID
FileAppend, [DEBUG] No valid link arg, using default Drive ID`n, %UpdaterLog%
}
ZipPass := (SourceHost = "pixeldrain") ? "" : "1"
FileAppend, [%A_Now%] Host=%SourceHost% FileID=%FileID% ZipPass=%ZipPass%`n, %UpdaterLog%
UpdateDir  := A_ScriptDir . "\update"
ZipFile    := UpdateDir . "\update.zip"
ExtractDir := A_ScriptDir
TempPS     := UpdateDir . "\dl.ps1"
ProgressFile := UpdateDir . "\progress.txt"
IfNotExist, %UpdateDir%
FileCreateDir, %UpdateDir%
IfExist, %ZipFile%
FileDelete, %ZipFile%
IfExist, %ProgressFile%
FileDelete, %ProgressFile%
Gui, Prog:New, +AlwaysOnTop -MinimizeBox -MaximizeBox, Đang cập nhật...
Gui, Prog:Font, s10 Bold, Segoe UI
Gui, Prog:Add, Text, x20 y15 w360 vLabelStatus, Đang chuẩn bị tải...
Gui, Prog:Font, s9 Norm, Segoe UI
Gui, Prog:Add, Progress, x20 y45 w360 h22 vMyProgress Range0-100, 0
Gui, Prog:Add, Text, x20 y75 w360 vLabelDetail, 0 MB / ?? MB
Gui, Prog:Font, s7 Norm, Segoe UI
Gui, Prog:Add, Text, x300 y95 w80 Right cGray, v%UpdaterVersion%
Gui, Prog:Show, w400 h115
PSScript =
(
$id = "%FileID%"
$host_ = "%SourceHost%"
$dest = "%ZipFile%"
$progFile = "%ProgressFile%"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

"0|Đang kết nối đến máy chủ..." | Set-Content $progFile

if ($host_ -eq "pixeldrain") {
    $url2 = "https://pixeldrain.com/api/file/$id`?download"
} else {
    $url2 = "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t&authuser=0"
}

"0|Đang tải file..." | Set-Content $progFile

$req = [Net.HttpWebRequest]::Create($url2)
$req.UserAgent = "Mozilla/5.0"
$resp2 = $req.GetResponse()
$total = $resp2.ContentLength
$stream = $resp2.GetResponseStream()
$fs = [IO.File]::Create($dest)
$buf = New-Object byte[] 65536
$downloaded = 0
while (($read = $stream.Read($buf, 0, $buf.Length)) -gt 0) {
    $fs.Write($buf, 0, $read)
    $downloaded += $read
    if ($total -gt 0) {
        $pct = [int]($downloaded * 100 / $total)
        $dlMB = [math]::Round($downloaded/1MB, 1)
        $totMB = [math]::Round($total/1MB, 1)
        "$pct|Đang tải... $dlMB MB / $totMB MB" | Set-Content $progFile
    }
}
$fs.Close()
$stream.Close()
"100|Tải xong!" | Set-Content $progFile
)
FileDelete, %TempPS%
FileAppend, %PSScript%, %TempPS%
Run, powershell -NoProfile -ExecutionPolicy Bypass -File "%TempPS%",, Hide, dlPID
Loop {
Sleep, 300
IfNotExist, %ProgressFile%
Continue
FileReadLine, line, %ProgressFile%, 1
If (line = "")
Continue
pct  := SubStr(line, 1, InStr(line, "|") - 1)
msg  := SubStr(line, InStr(line, "|") + 1)
GuiControl, Prog:, MyProgress, %pct%
GuiControl, Prog:, LabelDetail, %msg%
If (pct >= 100)
Break
Process, Exist, %dlPID%
If (!ErrorLevel) {
Sleep, 200
FileReadLine, line, %ProgressFile%, 1
pct := SubStr(line, 1, InStr(line, "|") - 1)
msg := SubStr(line, InStr(line, "|") + 1)
GuiControl, Prog:, MyProgress, %pct%
GuiControl, Prog:, LabelDetail, %msg%
Break
}
}
FileDelete, %TempPS%
FileDelete, %ProgressFile%
IfNotExist, %ZipFile%
{
GuiControl, Prog:, LabelStatus, Lỗi tải file!
GuiControl, Prog:, LabelDetail, Không tìm thấy file sau khi tải.
Sleep, 2000
Gui, Prog:Destroy
MsgBox, 16, Lỗi, Không tải được file!`nKiểm tra link Drive có public không?
Return
}
FileGetSize, fSize, %ZipFile%
If (fSize < 10000)
{
Gui, Prog:Destroy
MsgBox, 16, Lỗi, File tải về quá nhỏ - Drive có thể đang chặn.
Return
}
GuiControl, Prog:, LabelStatus, Đang giải nén...
GuiControl, Prog:, LabelDetail, Vui lòng chờ...
GuiControl, Prog:, MyProgress, 0
SevenZip := A_ScriptDir . "\\tools\\7z.exe"
IfNotExist, %SevenZip%
{
FileAppend, [%A_Now%] tools\\7z.exe not found, fallback to system 7-Zip`n, %UpdaterLog%
SevenZip := "C:\\Program Files\\7-Zip\\7z.exe"
}
IfNotExist, %SevenZip%
{
FileAppend, [%A_Now%] ERROR: 7-Zip khong ton tai`n, %UpdaterLog%
Gui, Prog:Destroy
MsgBox, 16, Lỗi, Không tìm thấy 7-Zip để giải nén!
Return
}
UnzipLog := UpdateDir . "\\unzip.log"
TempUnzipCmd := UpdateDir . "\\unzip.cmd"
FileDelete, %TempUnzipCmd%
If (ZipPass != "") {
FileAppend,
    (L Trim
    @echo off
    "%SevenZip%" x "%ZipFile%" -p%ZipPass% -o"%UpdateDir%" -y > "%UnzipLog%" 2>&1
    echo EXITCODE=`%ERRORLEVEL`% >> "%UnzipLog%"
), %TempUnzipCmd%
} Else {
FileAppend,
    (L Trim
    @echo off
    "%SevenZip%" x "%ZipFile%" -o"%UpdateDir%" -y > "%UnzipLog%" 2>&1
    echo EXITCODE=`%ERRORLEVEL`% >> "%UnzipLog%"
), %TempUnzipCmd%
}
Run, "%TempUnzipCmd%",, Hide, unzipPID
fakeP := 0
Loop {
Sleep, 500
Process, Exist, %unzipPID%
If (!ErrorLevel)
Break
If (fakeP < 50)
fakeP += 4
Else If (fakeP < 70)
fakeP += 2
Else If (fakeP < 90)
fakeP += 1
GuiControl, Prog:, MyProgress, %fakeP%
GuiControl, Prog:, LabelDetail, Đang giải nén... (%fakeP%`%)
}
Process, WaitClose, %unzipPID%, 300
FileRead, UnzipOut, %UnzipLog%
If (InStr(UnzipOut, "EXITCODE=0") = 0 || InStr(UnzipOut, "Everything is Ok") = 0)
{
Gui, Prog:Destroy
MsgBox, 16, Lỗi, Giải nén thất bại! (sai mật khẩu hoặc ZIP bỏng)`nChi tiết: %UnzipLog%
Return
}
FileDelete, %TempUnzipCmd%
GuiControl, Prog:, MyProgress, 100
GuiControl, Prog:, LabelDetail, Giải nén hoàn tất!
Sleep, 600
TempPS2 := UpdateDir . "\move.ps1"
FileDelete, %TempPS2%
PSMove =
(
$updateDir = "%UpdateDir%"
$dest = "%ExtractDir%"

$TLMToolFolder = Get-ChildItem -Path $updateDir -Directory | Where-Object { $_.Name -like "TLMTool*" } | Select-Object -First 1

if ($TLMToolFolder) {
    $distFolder = Join-Path $TLMToolFolder.FullName "TLMTool.dist"

    if (Test-Path $distFolder) {
        # Copy tất cả trừ update.exe
        robocopy $distFolder $dest /E /XF update.exe /R:1 /W:1 /NFL /NDL /NJH /NJS

        # Chép update.exe mới vào update\ để bootstrap dùng
        $newUpdater = Join-Path $distFolder "update.exe"
        if (Test-Path $newUpdater) {
            Copy-Item $newUpdater -Destination $updateDir -Force
        }

        # Xóa folder TLMTool*
        cmd /c "rd /s /q `"$($TLMToolFolder.FullName)`""
    } else {
        "ERROR: Khong tim thay TLMTool.dist trong $($TLMToolFolder.FullName)" | Out-File "$updateDir\error.log"
    }
} else {
    "ERROR: Khong tim thay folder TLMTool* trong $updateDir" | Out-File "$updateDir\error.log"
}
)
FileAppend, %PSMove%, %TempPS2%
GuiControl, Prog:, LabelStatus, Đang cập nhật file...
GuiControl, Prog:, LabelDetail, Vui lòng chờ...
GuiControl, Prog:, MyProgress, 0
Run, powershell -NoProfile -ExecutionPolicy Bypass -File "%TempPS2%",, Hide, movePID
fakeP := 0
Loop {
Sleep, 400
Process, Exist, %movePID%
If (!ErrorLevel)
Break
If (fakeP < 70)
fakeP += 3
Else If (fakeP < 90)
fakeP += 1
GuiControl, Prog:, MyProgress, %fakeP%
GuiControl, Prog:, LabelDetail, Đang di chuyển file... (%fakeP%`%)
}
Process, WaitClose, %movePID%, 60
IfExist, %UpdateDir%\error.log
{
Gui, Prog:Destroy
MsgBox, 16, Lỗi, Không tìm thấy cấu trúc thư mục trong ZIP!`nXem chi tiết: %UpdateDir%\error.log
Return
}
GuiControl, Prog:, MyProgress, 100
GuiControl, Prog:, LabelDetail, Cập nhật hoàn tất!
Sleep, 600
FileDelete, %TempPS2%
FileDelete, %ZipFile%
NewUpdaterInUpdate := UpdateDir . "\update.exe"
FileAppend, [%A_Now%] NewUpdaterInUpdate=%NewUpdaterInUpdate%`n, %UpdaterLog%
If (FileExist(NewUpdaterInUpdate))
{
BootstrapExe := A_ScriptDir . "\bootstrap.exe"
ThisExe      := A_ScriptDir . "\update.exe"
FileAppend, [%A_Now%] Running bootstrap...`n, %UpdaterLog%
If (FileExist(BootstrapExe))
Run, "%BootstrapExe%" "%NewUpdaterInUpdate%" "%ThisExe%",, Hide
Else
FileAppend, [%A_Now%] ERROR: bootstrap.exe not found`n, %UpdaterLog%
} Else {
FileAppend, [%A_Now%] No new update.exe found, skipping bootstrap`n, %UpdaterLog%
}
GuiControl, Prog:, LabelStatus, Hoàn tất!
GuiControl, Prog:, LabelDetail, Đang khởi động lại...
GuiControl, Prog:, MyProgress, 100
Sleep, 1000
Gui, Prog:Destroy
Run, %A_ScriptDir%\TLMTool.exe
ExitApp