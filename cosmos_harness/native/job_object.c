/*
 * L7 process tree. Language: C, because this is the Win32 job API.
 *
 * Creates an unnamed job, sets kill-on-job-close and an active-process
 * limit, reads the flags back, and closes the handle. It does not assign
 * the current process. Assigning this process would kill the harness when
 * the handle closes. Child assignment lives in job.py run_child.
 *
 * wipe_proof stays false. A job without a restricted token, a denied
 * network, and a measured child is not a filesystem jail. Path policy is
 * cosmos_harness/jail.py. This program prints policy_only either way so a
 * green exit cannot be read as a wipe-proof enclosure.
 *
 * Build (optional):
 *   cl /nologo /W4 native\job_object.c
 *   job_object.exe
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>

int main(void) {
    HANDLE job = CreateJobObjectW(NULL, NULL);
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION info;
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION back;
    DWORD wanted;

    if (job == NULL) {
        printf("policy_only\n");
        return 0;
    }
    ZeroMemory(&info, sizeof info);
    wanted = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS;
    info.BasicLimitInformation.LimitFlags = wanted;
    info.BasicLimitInformation.ActiveProcessLimit = 4;
    if (!SetInformationJobObject(job, JobObjectExtendedLimitInformation, &info, sizeof info)) {
        CloseHandle(job);
        printf("policy_only\n");
        return 0;
    }
    ZeroMemory(&back, sizeof back);
    if (!QueryInformationJobObject(
            job, JobObjectExtendedLimitInformation, &back, sizeof back, NULL)) {
        CloseHandle(job);
        printf("policy_only\n");
        return 0;
    }
    CloseHandle(job);
    if ((back.BasicLimitInformation.LimitFlags & wanted) != wanted) {
        printf("policy_only\n");
        return 0;
    }
    /* Flags matched. Still not wipe-proof. */
    printf("policy_only\n");
    return 0;
}
