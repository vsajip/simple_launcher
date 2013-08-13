/*
 * Copyright (C) 2011-2013 Vinay Sajip. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include "stdafx.h"

#define MSGSIZE 1024

static char suffix[] = {
#if defined(_CONSOLE)
    "-script.py"
#else
    "-script.pyw"
#endif
};

static int pid = 0;

#if !defined(_CONSOLE)

typedef int (__stdcall *MSGBOXWAPI)(IN HWND hWnd, 
        IN LPCSTR lpText, IN LPCSTR lpCaption, 
        IN UINT uType, IN WORD wLanguageId, IN DWORD dwMilliseconds);

#define MB_TIMEDOUT 32000

int MessageBoxTimeoutA(HWND hWnd, LPCSTR lpText, 
    LPCSTR lpCaption, UINT uType, WORD wLanguageId, DWORD dwMilliseconds)
{
    static MSGBOXWAPI MsgBoxTOA = NULL;
    HMODULE hUser = LoadLibraryA("user32.dll");

    if (!MsgBoxTOA) {
        if (hUser)
            MsgBoxTOA = (MSGBOXWAPI)GetProcAddress(hUser, 
                                      "MessageBoxTimeoutA");
        else {
            //stuff happened, add code to handle it here 
            //(possibly just call MessageBox())
        }
    }

    if (MsgBoxTOA)
        return MsgBoxTOA(hWnd, lpText, lpCaption, uType, wLanguageId,
                         dwMilliseconds);
    if (hUser)
        FreeLibrary(hUser);
    return 0;
}

#endif

static void
assert(BOOL condition, char * format, ... )
{
    if (!condition) {
        va_list va;
        char message[MSGSIZE];
        int len;

        va_start(va, format);
        len = vsnprintf(message, MSGSIZE - 1, format, va);
#if defined(_CONSOLE)
        fprintf(stderr, "Fatal error in launcher: %s\n", message);
#else
        MessageBoxTimeoutA(NULL, message, "Fatal Error in Launcher",
                           MB_OK | MB_SETFOREGROUND | MB_ICONERROR,
                           0, 2000);
#endif
        ExitProcess(1);
    }
}

static char *
skip_ws(char *p)
{
    while (*p && isspace(*p))
        ++p;
    return p;
}

static char *
skip_me(char * p)
{
    char * result;
    char terminator;

    if (*p != '\"')
        terminator = ' ';
    else {
        terminator = *p++;
        ++p;
    }
    result = strchr(p, terminator);
    if (result == NULL) /* perhaps nothing more on the command line */
        result = "";
    else
        result = skip_ws(++result);
    return result;
}

static char *
find_terminator(char *buffer, size_t size)
{
    char c;
    char * result = NULL;
    char * end = buffer + size;
    char * p;

    for (p = buffer; p < end; p++) {
        c = *p;
        if (c == '\r') {
            result = p;
            break;
        }
        if (c == '\n') {
            result = p;
            break;
        }
    }
    return result;
}

static BOOL
safe_duplicate_handle(HANDLE in, HANDLE * pout)
{
    BOOL ok;
    HANDLE process = GetCurrentProcess();
    DWORD rc;

    *pout = NULL;
    ok = DuplicateHandle(process, in, process, pout, 0, TRUE,
                         DUPLICATE_SAME_ACCESS);
    if (!ok) {
        rc = GetLastError();
        if (rc == ERROR_INVALID_HANDLE)
            ok = TRUE;
    }
    return ok;
}

static BOOL
control_key_handler(DWORD type)
{
    if ((type == CTRL_C_EVENT) && pid)
        GenerateConsoleCtrlEvent(pid, 0);
    return TRUE;
}

static void
run_child(char * cmdline)
{
    HANDLE job;
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION info;
    DWORD rc;
    BOOL ok;
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    job = CreateJobObject(NULL, NULL);
    ok = QueryInformationJobObject(job, JobObjectExtendedLimitInformation,
                                  &info, sizeof(info), &rc);
    assert(ok && (rc == sizeof(info)), "Job information querying failed");
    info.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
                                             JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK;
    ok = SetInformationJobObject(job, JobObjectExtendedLimitInformation, &info,
                                 sizeof(info));
    assert(ok, "Job information setting failed");
    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    ok = safe_duplicate_handle(GetStdHandle(STD_INPUT_HANDLE), &si.hStdInput);
    assert(ok, "stdin duplication failed");
    ok = safe_duplicate_handle(GetStdHandle(STD_OUTPUT_HANDLE), &si.hStdOutput);
    assert(ok, "stdout duplication failed");
    ok = safe_duplicate_handle(GetStdHandle(STD_ERROR_HANDLE), &si.hStdError);
    assert(ok, "stderr duplication failed");
    si.dwFlags = STARTF_USESTDHANDLES;
    SetConsoleCtrlHandler((PHANDLER_ROUTINE) control_key_handler, TRUE);
    ok = CreateProcess(NULL, cmdline, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    assert(ok, "Unable to create process using '%s'", cmdline);
    pid = pi.dwProcessId;
    AssignProcessToJobObject(job, pi.hProcess);
    CloseHandle(pi.hThread);
    WaitForSingleObject(pi.hProcess, INFINITE);
    ok = GetExitCodeProcess(pi.hProcess, &rc);
    assert(ok, "Failed to get exit code of process");
    ExitProcess(rc);
}

static int
process(int argc, char * argv[])
{
    char * cmdline = skip_me(GetCommandLine());
    char me[MAX_PATH];
    char * pme;
    char * p;
    size_t len = GetModuleFileName(NULL, me, MAX_PATH);

    FILE *fp = NULL;
    char buffer[MAX_PATH];
    char *cp;
    char * cmdp;

    if (me[0] != '\"')
        pme = me;
    else {
        pme = &me[1];
        len -= 2;
    }
    pme[len] = '\0';

    /* Replace the .exe with -script.py(w) */
    p = strstr(pme, ".exe");
    assert(p != NULL, "Failed to find \".exe\" in executable name");

    len = MAX_PATH - (p - me);
    assert(len > sizeof(suffix), "Failed to append \"%s\" suffix", suffix);
    strncpy(p, suffix, sizeof(suffix));
    fp = fopen(pme, "rb");
    assert(fp != NULL, "Failed to open script file \"%s\"",
           pme);
    fread(buffer, sizeof(char), MAX_PATH, fp);
    fclose(fp);
    cp = find_terminator(buffer, MAX_PATH);
    assert(cp != NULL, "Expected to find terminator in shebang line");
    *cp = '\0';
    cp = buffer;
    while (*cp && isspace(*cp))
        ++cp;
    assert(*cp == '#', "Expected to find \'#\' at start of shebang line");
    ++cp;
    while (*cp && isspace(*cp))
        ++cp;
    assert(*cp == '!', "Expected to find \'!\' following \'#\' in shebang line");
    ++cp;
    while (*cp && isspace(*cp))
        ++cp;
    len = strlen(cp) + 3 + strlen(pme) + strlen(cmdline);   /* 2 spaces + NUL */
    cmdp = calloc(len, sizeof(char));
    assert(cmdp != NULL, "Expected to be able to allocate command line memory");
    _snprintf(cmdp, len, "%s %s %s", cp, pme, cmdline);
    run_child(cmdp);
    free(cmdp);
	return 0;
}

#if defined(_CONSOLE)

int main(int argc, char* argv[])
{
    return process(argc, argv);
}

#else

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                     LPSTR lpCmdLine, int nCmdShow)
{
    return process(__argc, __argv);
}
#endif