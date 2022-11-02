/*
Alexander Coxe
FFA@CEBAF - Corrector feedback, optimization and design

This file contains sampling algorithm(s) and probability distributions
it will be wrapped into the overall MCMC simulation as a header


gauss is a normal distribution with a mean of 0,

unif is a uniform distribution centered around zero

oned_sample is an application of the classic Metropolis-Hastings algorithm,
    (although it produces a certain number of points, no matter how many trials it takes)
    Arguments:
        distribution function,
        'extent' parameter for the given distribution,
        number of points to produce,
        and a step size between iterations.

MCnd is repeated application of oned_sample to N uncorrelated dimensions.
    As arguments it takes the parameters required for oned_sample, as well as the 
    number of dimensions.
*/

// include the standard libraries
#ifndef MetMC
#define MetMC

#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <cmath>
#include <complex>
#include <Eigen/Core>
#include <Eigen/Dense>



/*
Function Declarations
*/
double gauss(double x, double sigma);// Gaussian dist centered at 0
double unif(double x, double end);// uniform dist centered at 0

// Metropolis sampling in one dimension
Eigen::ArrayX<double> oned_sample(double (*f)(double, double) /*input the probability distrubution*/,
                                  double param /*std deviation or endpoint of symmetrical uniform dist*/,
                                  int Nmax, double h /*function takes step size as an argument*/);

// Metropolis sampling for NE uncorrelated dimensions, using the same probability dist
Eigen::ArrayXXd MCnd(int NE /*number of lattice parameters (eg mag length, field strength, etc) to generate*/,
                     double (*f)(double, double) /*distribution to use*/, double param /*distribution parameter*/,
                     int Ns /*number of distinct 'offsets'*/, double hE /*elementwise step size*/);




// Normal distribution symmetric around zero
// with std dev sigma
double gauss(double x, double sigma){

    double p = exp(-.5 * pow((x) / sigma, 2)) / (sigma * sqrt(2. * M_PI)); // probability calculation

    return p;
}


// uniform dist centered at zero with extent 2*end
double unif(double x, double end){

    if(-end <= x && x <= end) return 1/(2*end);

    else return 0;
}

// this function is a 1d metropolis sampler;
// I plan to implement it for each dimension of my simulation, for however many lattices I want.
Eigen::ArrayX<double> oned_sample(double (*f)(double, double) /*input the probability distrubution*/,
                                  double param /*std deviation or endpoint of symmetrical uniform dist*/,
                                  int Nmax, double h /*function takes step size as an argument*/)
{

    // loop variables
    //	int Nmax = 10000000;//maximum number of steps
    double x = 0; // distributed points, value changes each accepted iteration
    double y = 0; // previous value for checking acceptance
    int count = 0;
    // metropolis params and variables
    double u; // variable which stores random numbers for metropolis step in x
    double z; // divide distribution points
    double a; // derivative size limiter

    // return array which will contain all mc steps
    Eigen::ArrayX<double> seq(Nmax);

    // initialize random number generator
    std::srand(std::time(0));

    // loop over the metropolis algorithm
    while (count < Nmax)
    {
        u = std::rand() / (RAND_MAX + 1.); // random num
        x = y + h * (2 * u - 1.);          // random step size

        a = std::rand() / (RAND_MAX + 1.); // randomly sized number for accepting/rejecting step

        z = f(x, param) / f(y, param); // ratio of new prob/old prob

        if (z < a)
            continue; // accept/reject metropolis step

        seq(count) = x;
        y = x; // change the previous accepted step

        count++;
    }

    return seq;
}

// Extension of oned_sampler to N uncorrelated dimensions
Eigen::ArrayXXd MCnd(int NE /*number of lattice elements considered*/,
                     double (*f)(double, double) /*distribution to use*/, double param /*distribution parameter*/,
                     int Ns /*number of distinct 'offsets'*/, double hE /*elementwise step size*/)
{

    Eigen::ArrayXX<double> lassy(Ns, NE); // store last iteration for testing

    for (int i = 0; i < NE; i++)
    {
        lassy.col(i) = oned_sample(f, param, Ns, hE);
    }

    return lassy;
}


#endif