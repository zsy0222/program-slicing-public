#include<stdio.h>
long long int arr[250000];
int compare(const void *pa,const void *pb){
    long long int a=*(const long long int*)pa;
    long long int b=*(const long long int*)pb;
    if(a<b) return -1;
    if(a>b) return 1;
    return 0;
}
int main(int argc, char *argv[]){
int a,b,c,d,e;
scanf("%d%d",&a,&b);
int i;
for(i=0;i<a*2;i++){
        scanf("%lld",arr+i);
}
qsort(arr,a*2,sizeof(long long int),compare);
if((arr[a]*a+(arr[a]/2.0*a)) <= b && arr[0]>=arr[a]/2.0)
printf("%lf", arr[a]*a + arr[0]/2.0*a);
else if(((arr[0]*a) + ((2*arr[0])*a))<=b && arr[a]>=2*arr[0])
printf("%lld",((arr[0]*a) + ((2*arr[0])*a)));
else printf("%lf",(double)b);
}