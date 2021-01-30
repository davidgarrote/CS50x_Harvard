#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    // Iterating over each pixel represented in the 2 dimensional array

    for (int i = 0; i < height; i++)
        {
        for (int j = 0;  j < width ;j++)
            {
            // Average of Rbg in image[i][j] set to rgbtGrey
            float rgbtGray = round((image[i][j].rgbtRed + image[i][j].rgbtBlue + image[i][j].rgbtGreen) / 3.000);

            //Setting averaged values to rgbt
            image[i][j].rgbtRed = rgbtGray;
            image[i][j].rgbtGreen = rgbtGray;
            image[i][j].rgbtBlue = rgbtGray;
            }
        }

    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    // Formula
    // sepiaRed = .393 * originalRed + .769 * originalGreen + .189 * originalBlue
    // sepiaGreen = .349 * originalRed + .686 * originalGreen + .168 * originalBlue
    // sepiaBlue = .272 * originalRed + .534 * originalGreen + .131 * originalBlue

        // Iterating over each pixel represented in the 2 dimensional array

        for (int i = 0; i < height; i++)
        {
            for (int j = 0;  j < width ;j++)
             {

                // Assigning the original values to OriginalColour
                float originalRed = image[i][j].rgbtRed;
                float originalGreen = image[i][j].rgbtGreen;
                float originalBlue = image[i][j].rgbtBlue;

                //Calculating Sepia formula
                float sepiaRed = round(.393 * originalRed + .769 * originalGreen + .189 * originalBlue);
                float sepiaGreen = round(.349 * originalRed + .686 * originalGreen + .168 * originalBlue);
                float sepiaBlue = round(.272 * originalRed + .534 * originalGreen + .131 * originalBlue);

                //Making sure no values pass 255
                if (sepiaRed > 255)
                {
                    sepiaRed = 255;
                }
                if (sepiaGreen > 255)
                {
                    sepiaGreen = 255;
                }
                if (sepiaBlue > 255)
                {
                    sepiaBlue = 255;
                }

                //Assigning new values to rgbt's for new photo
                image[i][j].rgbtRed = sepiaRed;
                image[i][j].rgbtGreen = sepiaGreen;
                image[i][j].rgbtBlue = sepiaBlue;

             }
        }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{

   int tmp[3];
   for (int i = 0; i < height; i++)

        {
            for (int j = 0;  j < width / 2 ;j++)
            {
                tmp[0]= image[i][j].rgbtRed;
                tmp[1]= image[i][j].rgbtGreen;
                tmp[2]= image[i][j].rgbtBlue;

                // swap pixels with the ones on the opposite side of the picture and viceversa
                image[i][j].rgbtBlue = image[i][width - j - 1].rgbtBlue;
                image[i][j].rgbtGreen = image[i][width - j - 1].rgbtGreen;
                image[i][j].rgbtRed = image[i][width - j - 1].rgbtRed;

                image[i][width - j - 1].rgbtBlue = tmp[2];
                image[i][width - j - 1].rgbtGreen = tmp[1];
                image[i][width - j - 1].rgbtRed = tmp[0];
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    int sumBlue;
    int sumGreen;
    int sumRed;
    float counter;
    //create a temporary table of colors to not alter the calculations
    RGBTRIPLE temp[height][width];

    for (int i = 0; i < width; i++)
    {
        for (int j = 0; j < height; j++)
        {
            sumBlue = 0;
            sumGreen = 0;
            sumRed = 0;
            counter = 0.00;

            // sums values of the pixel and 8 neighboring ones, skips iteration if it goes outside the pic
            for (int k = -1; k < 2; k++)
            {
                if (j + k < 0 || j + k > height - 1)
                {
                    continue;
                }

                for (int h = -1; h < 2; h++)
                {
                    if (i + h < 0 || i + h > width - 1)
                    {
                        continue;
                    }

                    sumBlue += image[j + k][i + h].rgbtBlue;
                    sumGreen += image[j + k][i + h].rgbtGreen;
                    sumRed += image[j + k][i + h].rgbtRed;
                    counter++;
                }
            }

            // averages the sum to make picture look blurrier
            temp[j][i].rgbtBlue = round(sumBlue / counter);
            temp[j][i].rgbtGreen = round(sumGreen / counter);
            temp[j][i].rgbtRed = round(sumRed / counter);
        }
    }

    //copies values from temporary table
    for (int i = 0; i < width; i++)
    {
        for (int j = 0; j < height; j++)
        {
            image[j][i].rgbtBlue = temp[j][i].rgbtBlue;
            image[j][i].rgbtGreen = temp[j][i].rgbtGreen;
            image[j][i].rgbtRed = temp[j][i].rgbtRed;
        }
    }
}
