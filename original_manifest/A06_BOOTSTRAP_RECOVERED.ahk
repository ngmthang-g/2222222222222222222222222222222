; <COMPILER: v1.1.37.02>
#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
argCount := A_Args.MaxIndex()
if (argCount = "")
argCount := 0
if (argCount < 2)
ExitApp
NewFile := A_Args[1]
TargetFile := A_Args[2]
Loop
{
if !FileExist(NewFile)
{
Sleep, 500
Continue
}
FileMove, %NewFile%, %TargetFile%, 1
if (!ErrorLevel)
break
Sleep, 500
}
ExitApp