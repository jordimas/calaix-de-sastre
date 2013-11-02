/*
    Shows that the thousands separator for Catalan language is incorrect 
*/

#include <stdio.h>
#include <locale.h>

void show()
{
    printf("Current locale: %s\n", setlocale(LC_ALL,NULL));
    printf("%'d\n", 1123456789);
}

int main(void)
{
    show();
    
    setlocale(LC_ALL, "es_US");
    show();
  
    setlocale(LC_ALL, "de_DE.UTF-8");
    show();
  
    setlocale(LC_ALL, "es_ES");
    show();

    setlocale(LC_ALL, "ca_ES");
    show();

    return 0;
}
