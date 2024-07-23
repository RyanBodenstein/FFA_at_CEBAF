
import re
import sys
import os

def p1(f1):
    with open(f1, 'r') as f2:
        c1 = f2.read()

    p_central_mev = re.search(r'p_central_mev=([\d.]+)', c1).group(1)
    emit_x = re.search(r'emit_x=([\de.-]+)', c1).group(1)
    emit_y = re.search(r'emit_y=([\de.-]+)', c1).group(1)
    beta_x = re.search(r'beta_x=([\d.]+)', c1).group(1)
    alpha_x = re.search(r'alpha_x=([\d.-]+)', c1).group(1)
    beta_y = re.search(r'beta_y=([\d.]+)', c1).group(1)
    alpha_y = re.search(r'alpha_y=([\d.-]+)', c1).group(1)

    energy_gev = float(p_central_mev) / 1000.0

    return {
        'energy': energy_gev,
        'emit_x': emit_x,
        'emit_y': emit_y,
        'beta_x': beta_x,
        'alpha_x': alpha_x,
        'beta_y': beta_y,
        'alpha_y': alpha_y
    }

def g1(p2):
    o1 = (
        'beam, particle="e-",\n'
        '      energy={energy}*GeV,\n'
        '      distrType="gausstwiss",\n'
        '      emitx={emit_x}*m,\n'
        '      emity={emit_y}*m,\n'
        '      betx={beta_x}*m,\n'
        '      bety={beta_y}*m,\n'
        '      alfx={alpha_x},\n'
        '      alfy={alpha_y},\n'
        '      distrType="gauss";'
    )

    return o1.format(
        energy=p2['energy'],
        emit_x=p2['emit_x'],
        emit_y=p2['emit_y'],
        beta_x=p2['beta_x'],
        alpha_x=p2['alpha_x'],
        beta_y=p2['beta_y'],
        alpha_y=p2['alpha_y']
    )

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        return

    f3 = sys.argv[1]
    if not os.path.isfile(f3):
        print(f"Error: {f3} does not exist.")
        return

    p3 = p1(f3)
    o2 = g1(p3)

    f4 = os.path.basename(f3)
    f5, _ = os.path.splitext(f4)
    f6 = f5.lower() + '_beam.gmad'

    with open(f6, 'w') as f7:
        f7.write(o2)

    print(f"Output written to {f6}")

if __name__ == '__main__':
    main()

