#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

int main (int argc, string argv[])
{
    // Only 2 arguments
    if (argc != 2)
    {
        printf("Usage: .ceasar key\n");
        return 1;
    }
    
    //converts string of the array to an int as k to check if number is positive
    int k = atoi(argv[1]);
    if(k < 0)
    {
        printf("Key must be positive\n");
        return 1;
    }
    
    //checks if the string contains non-numeric values
    
    int lenght = strlen(argv[1]);
    
    for (int r = 0; r < lenght; r++)
    {
        if (isdigit(argv[1][r]) == false)
        {
            return 1;
        }
    }
    
       string plaintext = get_string("plaintext: ");
       //loops over the plaintext and OUTPUT the ciphertext
       printf("ciphertext: ");
       for (int i = 0, len = strlen(plaintext); i < len; i++)
       {
           if (islower(plaintext[i]))
                printf("%c", (plaintext[i] - 'a' + k) % 26 + 'a');
           
           else if (isupper(plaintext[i]))
                printf("%c", (plaintext[i] - 'A' + k) % 26 + 'A');
           
           else
                printf("%c", plaintext[i]);
       }
        printf("\n");
    return 0;
}
