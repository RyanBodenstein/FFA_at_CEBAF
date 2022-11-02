#include <iostream>
#include <stdlib.h>
#include <string>


/*
The class 'EBF' contains all the information about
bending-focusing magnets in the east arc.
The private vars describe design parameters for 
the magnet, and the constructor builds with possible errors. 
Member functions print out the element definition (per Bmad) 
as well as the lattice entry.
*/
class EBF{
    double l = 1.295948029640486; // Chord length of magnet along arc in m
    double fld = -1.281505; // dipole field strength in T
    double grd = -68.55; // quadrupole gradient in T/m
    double theta = -0.031022985723386843; // bending angle of magnet in radians
    double xoff = 0, yoff = 0, zoff = 0; // magnet offsets in m
    
    public:

    /*Constructor function modifies default values*/
    EBF(double dl, double dx, double dy, double dz, double dang, double dfld, double dgrd){
        l += dl;
        fld += dfld;
        grd += dgrd;
        theta += dang;
        xoff += dx;
        yoff += dy;
        zoff += dz;
    }
};

class EBD{
    std::string id;
    double l = 0.9642533365019319;       // Chord length of magnet along arc in m
    double fld = -0.382754996;           // dipole field strength in T
    double grd = 72.4;                 // quadrupole gradient in T/m
    double theta = -0.006893971289796082; // bending angle of magnet in radians
    double xoff = 0, yoff = 0, zoff = 0; // magnet offsets in m

public:
    /*Constructor function modifies default values*/
    EBD(std::string name, double dl, double dx, double dy, double dz, double dang, double dfld, double dgrd)
    {
        id = name;
        l += dl;
        fld += dfld;
        grd += dgrd;
        theta += dang;
        xoff += dx;
        yoff += dy;
        zoff += dz;
    }

    std::string eledef(){
        std::cout << id << "_pin: patch, x_pitch = " << theta/2 << ", x_offset = " << 
            xoff << ", y_offset = " << yoff << ", z_offset = " << zoff << std::endl;
        std::cout << id << ": sbend, l = " << l << ", db_field = " << fld << ", "
    }
};