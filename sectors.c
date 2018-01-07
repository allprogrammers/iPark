#include <stdio.h>

int main(void)
{
    char buff[40];
    FILE* swcords = fopen("cord.txt","r");
    FILE* currentSector;
    int sector;
    char filename[40];
    while(fgets(buff,40,swcords))
    {
        double lat, lon;
        int ret =sscanf(buff,"Sector %d:",&sector) ;
        if(ret)
        {
            
            sprintf(filename,"Sector %d",sector);
            currentSector=fopen(filename,"w");
            printf("%d %d %s",ret,sector,buff);
            continue;
        }else
        {
            sscanf(buff,"%lf, %lf",&lat,&lon);
            printf("%lf,%lf",lat,lon);
            fputs(buff,currentSector);
        }
    }
    
}
