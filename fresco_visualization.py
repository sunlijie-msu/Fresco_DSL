import os
import re
from turtle import color
import matplotlib.pyplot as plt


# 1) Define a helper function for nuclear notation
#    e.g. "n14" -> "14N", "f17" -> "17F", "ne18" -> "18Ne", "c13" -> "13C"
def fix_nucl(notation):
    # Match digits (mass number) and letters (element)
    match = re.search(r'(\d+)', notation)
    if not match:
        # if no digits, just capitalize leftover
        return f"\\mathrm{{{notation.capitalize()}}}"  # e.g. "He"
    mass = match.group(1)  # e.g. "17"
    leftover = notation.replace(mass, "")  # e.g. "f"
    # e.g. leftover="f17" -> leftover="f"
    # Capitalize leftover (f->F, ne->Ne)
    leftover = leftover[0].upper() + leftover[1:].lower()
    return f"$^{{{mass}}}\\mathrm{{{leftover}}}$"

# 2) Regex to parse line like "n14(f17,ne18)c13 @ 170 MeV;"
reaction_pattern = re.compile(
    r'^\s*(\S+)\((\S+),(\S+)\)(\S+)\s*@\s*([\d\.]+)\s*MeV'
)
target = projectile = ejectile = recoil = None
beam_energy = None

# python3 fresco_visualization.py
os.system("export PATH=/home/sun/app/content/Frescoxex:$PATH")
os.chdir("/mnt/hgfs/Fresco_DSL/")
file_name = 'B5-example-tr'
infile = 'frescox_inputs/' + file_name + '.in'
outfile = 'frescox_outputs/' + file_name + '.out'
os.system("frescox < " + infile + " > " + outfile)

outfile = 'frescox_outputs/' + file_name + '_original.out'
with open(outfile) as f:
    lines = f.readlines()

elastic_angles, elastic_cross_sections, elastic_ratios = [], [], []
reaction_angles, reaction_cross_sections = [], []

i = 0
while i < len(lines):
    line = lines[i].strip()

    # (A) Attempt to parse the reaction line if not already found
    if target is None:  # only parse once
        m = reaction_pattern.search(line)
        if m:
            # parse raw strings, fix notation
            raw_target = fix_nucl(m.group(1))
            raw_proj   = fix_nucl(m.group(2))
            raw_eject  = fix_nucl(m.group(3))
            raw_recoil = fix_nucl(m.group(4))
            raw_beam   = float(m.group(5))
            target, projectile, ejectile, recoil = raw_target, raw_proj, raw_eject, raw_recoil
            beam_energy = raw_beam

    # (B) parse cross section lines
    if "deg.:" in line and "X-S" in line:
        # Example: " 0.90 deg.: X-S = 2.332519E+08 mb/sr,"
        tokens = line.split()
        angle  = float(tokens[0])     # e.g. "0.90"
        xsec   = float(tokens[4])     # e.g. "2.332519E+08"

        # Check next line for "/R"
        ratio = None
        if i+1 < len(lines):
            next_line = lines[i+1].strip()
            if "/R" in next_line:
                # => elastic block
                ratio_tokens = next_line.split()
                ratio = float(ratio_tokens[3])  # e.g. "/R = 1.017026E+00"
                i += 1  # consume that line

                elastic_angles.append(angle)
                elastic_cross_sections.append(xsec)
                elastic_ratios.append(ratio)
            else:
                # => other channels
                reaction_angles.append(angle)
                reaction_cross_sections.append(xsec)
        else:
            # end of file? treat as other channel if no next line
            reaction_angles.append(angle)
            reaction_cross_sections.append(xsec)
    i += 1

# Now we have:
#  elastic_angles, elastic_cross_section, elastic_ratio  => for part 1 (elastic, with /R)
#  reaction_angles, reaction_cross_section                  => for part 2 (other channels, no /R)
elastic_title = (
    f"Elastic: {target}({projectile},{projectile}){target} @ {beam_energy:.1f} MeV"
)
reaction_title = (
    f"Transfer: {target}({projectile},{ejectile}){recoil} @ {beam_energy:.1f} MeV"
)

# Example printout:
print("\nElastic Scattering (with /R):")
for a, xs, r in zip(elastic_angles, elastic_cross_sections, elastic_ratios):
    print(f"Angle={a} deg, X-S={xs} mb/sr, /R={r}")

print("\nReaction Channels (no /R):")
for a, xs in zip(reaction_angles, reaction_cross_sections):
    print(f"Angle={a} deg, X-S={xs} mb/sr")


# Plot the outputs
plt.rcParams['axes.linewidth'] = 2.0
plt.rcParams['font.size'] = 20
font_family_options = ['Times New Roman', 'Times', 'Cambria', 'Georgia', 'Courier New', 'serif']
plt.rcParams['font.family'] = font_family_options
# plt.rcParams['mathtext.default'] = 'regular'
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Times New Roman'
plt.rcParams['mathtext.it'] = 'Times New Roman:italic'


fig, axes = plt.subplots(1, 2, figsize=(15,5.6)) # 1 row, 2 columns
fig.subplots_adjust(left=0.09, bottom=0.18, right=0.98, top=0.90)

# Left subplot: ratio vs. angle (elastic)
axes[0].plot(elastic_angles, elastic_ratios, color='red', linewidth=2.0)
axes[0].set_xlabel(r'$\theta_{cm}$ (deg)')
axes[0].set_ylabel(r'd$\sigma_{el}/d\sigma_{Ru}$')
axes[0].set_yscale('log')
axes[0].set_title(elastic_title, fontsize=18)

# Right subplot: cross section vs. angle (other channels)
axes[1].plot(reaction_angles, reaction_cross_sections,
             color='dodgerblue', linewidth=2.0)
axes[1].set_xlabel(r'$\theta_{cm}$ (deg)')
axes[1].set_ylabel(r'd$\sigma_{tr}/d\Omega$ (mb/sr)')
axes[1].set_title(reaction_title, fontsize=18)

plt.savefig(file_name + '.png')
