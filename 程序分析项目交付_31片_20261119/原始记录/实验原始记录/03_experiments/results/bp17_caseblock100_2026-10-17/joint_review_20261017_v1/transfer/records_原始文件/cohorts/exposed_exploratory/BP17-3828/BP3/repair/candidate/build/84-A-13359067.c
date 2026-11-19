//
//  main.c
//  codeforces2
//
//  Created by Ashish on 10/1/15.
//  Copyright (c) 2015 Ashish. All rights reserved.
//

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include<math.h>

int main(int argc, char *argv[]) {
    int n;
    scanf("%d\n",&n);
    int i;
    i=n/2;
    int a[100005];
    scanf("%d",a+i);
    printf("%d\n", a[i]);
    
    return 0;
    }