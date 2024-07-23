import argparse
import os

def c1(b1):
    b2 = b1.lower()
    
    c2 = (
        f"include {b2}_lattice.gmad;\n"
        f"include {b2}_beam.gmad;\n"
        f"include {b2}_options.gmad;\n"
        "sample, all;\n"
    )
    
    o1 = f"{b2}.gmad"
    
    with open(o1, 'w') as f1:
        f1.write(c2)
    
    print(f"Output written to {o1}")

if __name__ == "__main__":
    p1 = argparse.ArgumentParser()
    p1.add_argument("name")
    
    a1 = p1.parse_args()
    
    c1(a1.name)

