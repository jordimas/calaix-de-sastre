/*
    This example shows a bug in %x date formatter

    When executed on ca_ES or es_ES locale this sample shows
    02/20/97 instead of the expected 20/02/97
    on libc version 2.29
*/

#include <glib.h>

int
main (void)
{
    char str_time[128]; 
    struct tm sample_tm;

    sample_tm.tm_sec	= 0;
    sample_tm.tm_min	= 0;
    sample_tm.tm_hour	= 0;
    sample_tm.tm_mday	= 20;
    sample_tm.tm_mon	= 1;
    sample_tm.tm_year	= 97;	
    sample_tm.tm_wday	= 0;
    sample_tm.tm_yday	= 0;
    sample_tm.tm_isdst  = 0;

    strftime(str_time, sizeof(str_time), "%x", &sample_tm); 
    g_print("%s\n", str_time);
    return 0;
}
