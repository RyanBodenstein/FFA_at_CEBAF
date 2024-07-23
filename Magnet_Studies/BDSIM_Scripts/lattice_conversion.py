import argparse
import os

def f1(p1):
    l1 = p1.get('L', '0.0')
    a1 = p1.get('ANGLE', '0.0')
    k1 = p1.get('K1', '0.0')
    e1 = p1.get('E1', '0.0')
    h1 = p1.get('HGAP', '0.0')
    f2 = p1.get('FINT', '0.0')
    e2 = p1.get('E2', '0.0')
    t1 = p1.get('TILT', '0.0')
    
    return (
        f"{p1['name'].lower()}: sbend, l={l1}, angle={a1}, "
        f"k1={k1}, e1={e1}, hgap={h1}, "
        f"fint={f2}, e2={e2}, tilt={t1};"
    )

def f2(p2):
    l2 = p2.get('L', '0.0')
    return f"{p2['name'].lower()}: drift, l={l2};"

def f3(p3):
    return f"{p3['name'].lower()}: marker;"

def f4(p4):
    l3 = p4.get('L', '0.0')
    h2 = p4.get('KICK', '0.0')
    return f"{p4['name'].lower()}: hkicker, l={l3}, hkick={h2};"

def f5(p5):
    l4 = p5.get('L', '0.0')
    v1 = p5.get('KICK', '0.0')
    return f"{p5['name'].lower()}: vkicker, l={l4}, vkick={v1};"

def f6(p6):
    l5 = p6.get('L', '0.0')
    k2 = p6.get('K1', '0.0')
    return f"{p6['name'].lower()}: quadrupole, l={l5}, k1={k2};"

ec = {
    "CSBEND": f1,
    "DRIFT": f2,
    "DRIF": f2,
    "MONITOR": f3,
    "MONI": f3,
    "HKICK": f4,
    "VKICK": f5,
    "KQUAD": f6,
}

def p7(f8):
    e7 = []
    e8 = {}
    with open(f8, 'r') as f9:
        for l6 in f9:
            if l6.strip() == "" or l6.strip().startswith("!"):
                continue
            l6 = l6.strip()
            if ":" in l6:
                if e8:
                    e7.append(e8)
                    e8 = {}
                
                while l6.endswith("&"):
                    l6 = l6[:-1] + next(f9).strip()

                n1, r1 = l6.split(":", 1)
                e8["name"] = n1.strip().strip('"')
                p8 = [p.strip().strip('"') for p in r1.split(",")]
                t2 = p8[0].strip().upper()
                if t2 in ec:
                    e8["type"] = t2
                elif t2.startswith("DRIF"):
                    e8["type"] = "DRIFT"
                else:
                    e8["type"] = t2
                
                for p9 in p8[1:]:
                    if "=" in p9:
                        k3, v2 = [p.strip() for p in p9.split("=")]
                        e8[k3] = v2.strip('"')
            else:
                p10 = [p.strip().strip('"') for p in l6.split(",")]
                for p11 in p10:
                    if "=" in p11:
                        k4, v3 = [p.strip() for p in p11.split("=")]
                        e8[k4] = v3.strip('"')
        
        if e8:
            e7.append(e8)
    
    return e7

def c7(e9):
    b2 = []
    for e10 in e9:
        c8 = ec.get(e10["type"])
        if c8:
            b2.append(c8(e10))
    return "\n".join(b2)

def p12(f10):
    l7 = None
    b3 = os.path.splitext(os.path.basename(f10))[0].upper()
    with open(f10, 'r') as f11:
        l8 = f11.readlines()
        for l9 in l8:
            l9 = l9.strip()
            if l9.startswith(f"{b3}: LINE="):
                l7 = l9.split(f"{b3}: LINE=")[1].strip()
            elif l7 is not None:
                if l9.endswith("&"):
                    l7 += l9.replace("&", "").strip()
                else:
                    l7 += l9.strip()
                if l9.endswith(")"):
                    break

    if l7:
        l7 = l7.replace("&", "").replace("(", "").replace(")", "")
        e11 = l7.split(",")
        
        m2 = 10
        f13 = []
        c9 = []
        for i2, e12 in enumerate(e11):
            e12 = e12.strip().lower()
            c9.append(e12)
            if len(c9) == m2 or i2 == len(e11) - 1:
                f13.append(", ".join(c9))
                c9 = []
        
        f14 = f"{b3.lower()}: line = (\n"
        for idx, l10 in enumerate(f13):
            if idx == len(f13) - 1:
                f14 += f"  {l10}\n"
            else:
                f14 += f"  {l10},\n"
        f14 += ");"
        
        return f14
    else:
        return f"No line section found in {f10}."

def main(f15):
    e13 = p7(f15)
    b4 = c7(e13)
    l11 = p12(f15)

    b5 = os.path.splitext(os.path.basename(f15))[0].lower()
    f16 = f"{b5}_lattice.gmad"

    with open(f16, 'w') as f17:
        f17.write(b4 + "\n\n")
        f17.write(l11 + "\n")
        f17.write(f"use, period={b5}\n")
    
    print(f"Combined output written to {f16}")

if __name__ == "__main__":
    p14 = argparse.ArgumentParser(description="Convert Elegant lattice file to BDSIM format")
    p14.add_argument("input_file", help="Path to the input Elegant lattice file (e.g., ARC1.lte)")
    
    a1 = p14.parse_args()
    main(a1.input_file)

