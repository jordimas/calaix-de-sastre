#include <glib.h>
#include <langinfo.h>

#define PREFERRED_DATE_FMT nl_langinfo (D_FMT)

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
