#Requires AutoHotkey v2.0
#SingleInstance Force

; Windows Explorer Goblin
; Ctrl + Space opens a smart rename overlay for the selected file/folder.
; Python suggestion brain lives in ../src/rename_brain.py.

global Goblin := Map(
    "active", false,
    "selectedPath", "",
    "dir", "",
    "fileName", "",
    "nameNoExt", "",
    "ext", "",
    "isFolder", false,
    "gui", "",
    "edit", "",
    "list", "",
    "status", "",
    "suggestions", [],
    "brain", A_ScriptDir "\..\src\rename_brain.py",
    "history", A_ScriptDir "\..\rename_history.jsonl"
)

#HotIf IsExplorerOrDesktop()
^Space::GoblinStart()
#HotIf

#HotIf Goblin["active"]
Tab::GoblinAcceptTop()
Enter::GoblinCommit()
Esc::GoblinCancel()
#HotIf

IsExplorerOrDesktop() {
    cls := WinGetClass("A")
    return cls = "CabinetWClass"
        || cls = "ExploreWClass"
        || cls = "Progman"
        || cls = "WorkerW"
}

GoblinStart() {
    global Goblin

    selectedPath := GetSelectedPathByClipboard()
    if selectedPath = "" {
        MsgBox("No file or folder selected.", "Explorer Goblin", "Iconi")
        return
    }

    SplitPath selectedPath, &fileName, &dir, &ext, &nameNoExt
    isFolder := DirExist(selectedPath) ? true : false

    Goblin["active"] := true
    Goblin["selectedPath"] := selectedPath
    Goblin["dir"] := dir
    Goblin["fileName"] := fileName
    Goblin["nameNoExt"] := nameNoExt
    Goblin["ext"] := ext
    Goblin["isFolder"] := isFolder
    Goblin["suggestions"] := []

    ShowGoblinGui(nameNoExt, isFolder, ext)
    GoblinUpdateSuggestions()
}

GetSelectedPathByClipboard() {
    oldClip := ClipboardAll()
    A_Clipboard := ""

    Send("^c")
    if !ClipWait(0.8) {
        A_Clipboard := oldClip
        return ""
    }

    path := Trim(A_Clipboard, "`r`n `t")
    A_Clipboard := oldClip

    if InStr(path, "`n") {
        path := StrSplit(path, "`n")[1]
        path := Trim(path, "`r`n `t")
    }

    if FileExist(path) || DirExist(path) {
        return path
    }
    return ""
}

ShowGoblinGui(initialText, isFolder, ext) {
    global Goblin

    g := Gui("+AlwaysOnTop +ToolWindow", "Explorer Goblin")
    g.MarginX := 12
    g.MarginY := 10
    g.SetFont("s10", "Segoe UI")

    title := isFolder ? "Rename folder" : "Rename file"
    g.AddText("w620", title)

    edit := g.AddEdit("vGoblinName w620", initialText)
    hint := isFolder ? "Folder mode" : "Extension preserved: ." ext
    g.AddText("w620 cGray", hint)

    list := g.AddListBox("vGoblinSuggestions w620 h170")
    status := g.AddText("w620 cGray", "Type to summon suggestions. Tab accepts top result. Enter renames.")

    btnUse := g.AddButton("w110", "Use Top")
    btnRename := g.AddButton("x+8 w110 Default", "Rename")
    btnCancel := g.AddButton("x+8 w110", "Cancel")

    Goblin["gui"] := g
    Goblin["edit"] := edit
    Goblin["list"] := list
    Goblin["status"] := status

    edit.OnEvent("Change", (*) => GoblinUpdateSuggestionsDebounced())
    list.OnEvent("DoubleClick", (*) => GoblinAcceptSelected())
    btnUse.OnEvent("Click", (*) => GoblinAcceptTop())
    btnRename.OnEvent("Click", (*) => GoblinCommit())
    btnCancel.OnEvent("Click", (*) => GoblinCancel())
    g.OnEvent("Close", (*) => GoblinCancel())
    g.OnEvent("Escape", (*) => GoblinCancel())

    MouseGetPos &mx, &my
    x := mx + 24
    y := my + 24
    g.Show("AutoSize x" x " y" y)
    edit.Focus()
    Send("^a")
}

GoblinUpdateSuggestionsDebounced() {
    SetTimer(GoblinUpdateSuggestions, 0)
    SetTimer(GoblinUpdateSuggestions, -120)
}

GoblinUpdateSuggestions(*) {
    global Goblin

    if !Goblin["active"] {
        return
    }

    typed := Goblin["edit"].Text
    if Trim(typed) = "" {
        GoblinSetSuggestions([])
        return
    }

    rows := CallBrain(typed)
    GoblinSetSuggestions(rows)
}

CallBrain(typed) {
    global Goblin

    reqFile := A_Temp "\explorer_goblin_request_" A_TickCount ".json"
    outFile := A_Temp "\explorer_goblin_response_" A_TickCount ".tsv"

    request := "{"
        . "`"typed`":" JsonString(typed) ","
        . "`"folder`":" JsonString(Goblin["dir"]) ","
        . "`"current_name`":" JsonString(Goblin["fileName"]) ","
        . "`"extension`":" JsonString(Goblin["ext"]) ","
        . "`"is_folder`":" (Goblin["isFolder"] ? "true" : "false") ","
        . "`"history_file`":" JsonString(Goblin["history"]) ","
        . "`"max_suggestions`":8"
        . "}"

    FileDeleteSafe(reqFile)
    FileDeleteSafe(outFile)
    FileAppend(request, reqFile, "UTF-8")

    brain := Goblin["brain"]
    cmd := 'py -3 "' brain '" --request "' reqFile '" --out "' outFile '"'

    try {
        RunWait(cmd, , "Hide")
    } catch Error as e {
        Goblin["status"].Text := "Python brain failed: " e.Message
        return []
    }

    if !FileExist(outFile) {
        Goblin["status"].Text := "No response from suggestion brain."
        return []
    }

    text := FileRead(outFile, "UTF-8")
    rows := []

    for line in StrSplit(text, "`n") {
        line := Trim(line, "`r`n")
        if line = "" {
            continue
        }
        parts := StrSplit(line, "`t")
        suggestion := parts.Length >= 1 ? parts[1] : ""
        score := parts.Length >= 2 ? parts[2] : ""
        reason := parts.Length >= 3 ? parts[3] : ""
        if suggestion != "" {
            rows.Push(Map("name", suggestion, "score", score, "reason", reason))
        }
    }

    FileDeleteSafe(reqFile)
    FileDeleteSafe(outFile)
    return rows
}

GoblinSetSuggestions(rows) {
    global Goblin

    Goblin["suggestions"] := rows
    lb := Goblin["list"]
    lb.Delete()

    if rows.Length = 0 {
        lb.Add(["(no suggestions)"])
        Goblin["status"].Text := "No suggestions yet. Keep typing."
        return
    }

    display := []
    for row in rows {
        display.Push(row["name"] "    [" row["reason"] "]")
    }
    lb.Add(display)
    lb.Value := 1
    Goblin["status"].Text := "Top suggestion: " rows[1]["name"]
}

GoblinAcceptTop(*) {
    global Goblin

    if !Goblin["active"] || Goblin["suggestions"].Length = 0 {
        return
    }

    Goblin["edit"].Text := Goblin["suggestions"][1]["name"]
    Goblin["edit"].Focus()
    Send("^a")
}

GoblinAcceptSelected(*) {
    global Goblin

    if !Goblin["active"] || Goblin["suggestions"].Length = 0 {
        return
    }

    idx := Goblin["list"].Value
    if idx < 1 || idx > Goblin["suggestions"].Length {
        return
    }

    Goblin["edit"].Text := Goblin["suggestions"][idx]["name"]
    Goblin["edit"].Focus()
    Send("^a")
}

GoblinCommit(*) {
    global Goblin

    if !Goblin["active"] {
        return
    }

    newBase := Trim(Goblin["edit"].Text)
    if newBase = "" {
        MsgBox("Name cannot be empty.", "Explorer Goblin", "Iconx")
        return
    }

    if RegExMatch(newBase, '[\\/:*?"<>|]') {
        MsgBox("Invalid Windows filename character detected.`n\ / : * ? `" < > |", "Explorer Goblin", "Iconx")
        return
    }

    oldPath := Goblin["selectedPath"]
    dir := Goblin["dir"]
    ext := Goblin["ext"]
    isFolder := Goblin["isFolder"]

    newPath := isFolder ? dir "\" newBase : dir "\" newBase "." ext

    if StrLower(oldPath) = StrLower(newPath) {
        GoblinClose()
        return
    }

    if FileExist(newPath) || DirExist(newPath) {
        MsgBox("That name already exists.", "Explorer Goblin", "Iconx")
        return
    }

    try {
        if isFolder {
            DirMove(oldPath, newPath)
        } else {
            FileMove(oldPath, newPath)
        }
        GoblinLearn(newBase)
        GoblinClose()
    } catch Error as e {
        MsgBox("Rename failed:`n" e.Message, "Explorer Goblin", "Iconx")
    }
}

GoblinLearn(name) {
    global Goblin

    reqFile := A_Temp "\explorer_goblin_learn_" A_TickCount ".json"
    outFile := A_Temp "\explorer_goblin_learn_" A_TickCount ".tsv"
    request := "{"
        . "`"typed`":" JsonString(name) ","
        . "`"learn`":" JsonString(name) ","
        . "`"history_file`":" JsonString(Goblin["history"])
        . "}"

    FileAppend(request, reqFile, "UTF-8")
    brain := Goblin["brain"]
    cmd := 'py -3 "' brain '" --request "' reqFile '" --out "' outFile '"'

    try RunWait(cmd, , "Hide")
    FileDeleteSafe(reqFile)
    FileDeleteSafe(outFile)
}

GoblinCancel(*) {
    GoblinClose()
}

GoblinClose() {
    global Goblin

    try Goblin["gui"].Destroy()
    Goblin["active"] := false
    Goblin["suggestions"] := []
}

JsonString(value) {
    s := value ""
    s := StrReplace(s, "\", "\\")
    s := StrReplace(s, '"', '\"')
    s := StrReplace(s, "`r", "\r")
    s := StrReplace(s, "`n", "\n")
    s := StrReplace(s, "`t", "\t")
    return '"' s '"'
}

FileDeleteSafe(path) {
    try {
        if FileExist(path) {
            FileDelete(path)
        }
    }
}
