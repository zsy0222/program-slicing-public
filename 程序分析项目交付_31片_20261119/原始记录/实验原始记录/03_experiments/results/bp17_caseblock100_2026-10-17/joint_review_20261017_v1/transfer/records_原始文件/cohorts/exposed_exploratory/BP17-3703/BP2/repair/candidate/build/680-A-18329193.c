#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define pi 3.1415926
#define rep(x,ini,end) for(x=(ini);x<(end);x++)
#define per(x,ini,end) for(x=(end-1);x>=(ini);x--)
#define max(x,y) ((x)>(y)?(x):(y))
#define min(x,y) ((x)<(y)?(x):(y))

int a[5] = {0};

void quickSort(int a[], int beginPos, int endPos)
{
    int i = beginPos, j = endPos;
    int flag = a[beginPos];
    if (beginPos>=endPos)
    {
        return;
    }

    while (i<j)
    {
        while ((a[j]>flag) && (i<j))
        {
            --j;
        }
        if (i == j)
        {
            break;
        }

        a[i] = a[j]; a[j] = flag;
        ++i;

        while ((a[i]<flag) && (i<j))
        {
            ++i;
        }
        if (i == j)
        {
            break;
        }

        a[j] = a[i]; a[i] = flag;
        --j;
    }

    quickSort(a, beginPos, i-1);
    quickSort(a, i+1, endPos);
}

int main(int argc, char *argv[])
{
    int i;
    int sum = 0;
    rep(i,0,5)
    {
        scanf("%d", &a[i]);
        sum = sum + a[i];
    }

    quickSort(a,0,4);

    int maxSum = 0;
    i = 0;
    while (i < 5)
    {
        int j = i;
        while (j < 5 && a[j] == a[i])
        {
            j++;
        }
        int cnt = j - i;
        if (cnt >= 3)
        {
            maxSum = max(maxSum, a[i] * cnt);
        }
        i = j;
    }

    int results = sum - maxSum;

    printf("%d\n", results);

    return 0;
}