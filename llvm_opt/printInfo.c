#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Declare the converted function with the correct mangled name
extern void _Z9addArraysiPfS_S_(int n, float* a, float* b, float* c);

int main() {
    int n = 100000; 
    float *a = malloc(n * sizeof(float)); 
    float *b = malloc(n * sizeof(float));  
    float *c = malloc(n * sizeof(float)); 

    // Initialize arrays
    for (int i = 0; i < n; i++) {
        a[i] = 2.0f;
        b[i] = 2.0f;
        c[i] = 1.0f;
    }

    // Measure execution time
    clock_t start = clock();
    
    _Z9addArraysiPfS_S_(n, a, b, c);
    
    clock_t end = clock();
    double cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;
    printf("Array size is %i \n", n);
    printf("Execution time: %f seconds\n", cpu_time_used);

    printf("Output: \n");
    // Print results (first 10 elements)
    for (int i = 0; i < 10; i++) {
        printf("%f ", c[i]);
    }
    printf("\n");

    free(a);
    free(b);
    free(c);

    return 0;
}