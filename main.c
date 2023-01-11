#include <stdio.h>

int sum(int x);
int sum(float x);

int main() {printf("%d\n", sum(1)); return 0;}

int sum(int x) {return x+1;}
