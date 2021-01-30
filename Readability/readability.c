#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    //Counting words
    char s[500];
    int words = 0, i;
 
    printf("Text: ");
    scanf("%[^\n]s", s);
    for (i = 0;s[i] != '\0';i++)
    {
        if (s[i] == ' ' && s[i+1] != ' ')
            words++;    
    }
    int num_words = (words + 1);
    // printf("%i words(s)\n", num_words);
    
    // Counting letters
    
    int letters = 0, h;
    
    scanf("%[^\n]s", s);
    for (h=0; s[h] != '\0';h++)
    {
        if ( islower(h[s]) || isupper(h[s]))
     letters++;
    }
    
    // printf("%i letters(s)\n", letters);
    
    //Counting sentencies
    
    int sentences = 0, j;
    
    scanf("%[^\n]s", s);
    for (j=0; s[j] != '\0'; j++)
    {
        if (s[j] == '.' || s[j] == '?' || s[j] == '!')
        sentences++;
    }
        // printf("%i sentence(s)\n", sentences);
        
        
        //calculating L, S and index
        
        float L = 1.0* letters/num_words * 100;
        float S = 1.0* sentences/num_words * 100;
        
        
        float index = 0.0588 * L - 0.296 * S - 15.8;
        
        //printing depending on grade
        
        if (16 <= index || index > 2 )
        {
        printf("Grade %.0f\n", index);
        }
        
        if ( index <1.0)
        {
            printf("Before Grade 1\n");
        }
       if (index>=16)
       {
            printf("Grade 16+\n");
       }
       
    }
