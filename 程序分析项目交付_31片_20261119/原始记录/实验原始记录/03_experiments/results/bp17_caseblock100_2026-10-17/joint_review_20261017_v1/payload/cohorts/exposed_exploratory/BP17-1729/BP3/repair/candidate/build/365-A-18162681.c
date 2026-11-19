#include<stdio.h>
int main(int argc, char *argv[])
{
	int n,k,x,i,r,j;
	scanf("%d%d",&n,&k);
	int c=0;
	for(i=0;i<n;i++)
	{
		scanf("%d",&x);
		int hash[10]={};
		while(x>0)
		{
			r=x%10;
			x/=10;
			hash[r]=1;
		}
		if(x==0)
		{
			int flag=1;
			for(j=0;j<=k;j++)
			{
				if(hash[j]==0)
					flag=0;
			}
			if(flag)
				c+=1;
		}
	}
	printf("%d\n",c);
	return 0;
}