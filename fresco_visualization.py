import os
import re
from turtle import color
import matplotlib.pyplot as plt


########################################
# Helper: Convert "n14" -> "$^{14}\\mathrm{N}$", etc.
########################################
def format_isotope(notation):
    match = re.search(r'(\d+)', notation)
    if not match:
        return f"\\mathrm{{{notation.capitalize()}}}"  # no digits => e.g. He
    mass = match.group(1)           # e.g. "17"
    leftover = notation.replace(mass, "")  # e.g. "f"
    leftover = leftover.capitalize()       # e.g. "f" -> "F"
    return f"$^{{{mass}}}\\mathrm{{{leftover}}}$"

########################################
# Regex for line like "n14(f17,ne18)c13 @ 170 MeV;"
########################################
reaction_pattern = re.compile(r'^\s*(\S+)\((\S+),(\S+)\)(\S+)\s*@\s*([\d\.]+)\s*MeV')

########################################
# Define input and output file
########################################
os.system("export PATH=/home/sun/app/content/Frescoxex:$PATH")
os.chdir("/mnt/hgfs/Fresco_DSL/")
# file_name = 'B1-example-el'
file_name = 'B5-example-tr' # modify

infile = f'frescox_inputs/{file_name}.in'
outfile = f'frescox_outputs/{file_name}.out'

########################################
# 1) Run Fresco
########################################
os.system(f"frescox < {infile} > {outfile}")

########################################
# 2) Read the first line of the input file
#    if we cannot find a reaction pattern.
########################################
with open(infile) as fi:
    first_line_in = fi.readline().strip()

########################################
# 3) Parse the output file
########################################
with open(outfile) as fo:
    lines = fo.readlines()

elastic_angles, elastic_cross_sections, elastic_ratios = [], [], []
reaction_angles, reaction_cross_sections = [], []

target = projectile = ejectile = recoil = None
beam_energy = None

i = 0
while i < len(lines):
    line = lines[i].strip() # strip() removes leading/trailing whitespace

    # (A) Attempt to parse reaction line (once only)
    if target is None:
        m = reaction_pattern.match(line)
        if m:
            # parse raw strings, fix notation
            raw_target = format_isotope(m.group(1))
            raw_proj   = format_isotope(m.group(2))
            raw_eject  = format_isotope(m.group(3))
            raw_recoil = format_isotope(m.group(4))
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
                # => elastic channels
                ratio_tokens = next_line.split()
                ratio = float(ratio_tokens[3])  # e.g. "/R = 1.017026E+00"
                i += 1  # consume that line

                elastic_angles.append(angle)
                elastic_cross_sections.append(xsec)
                elastic_ratios.append(ratio)
            else:
                # => reaction channels
                reaction_angles.append(angle)
                reaction_cross_sections.append(xsec)
                print("reaction_angle: ", angle, "reaction_cross_section: ", xsec)
        else:
            print(f"Warning: Could not parse angle/X-S in line: {line}")
            
    i += 1

########################################
# 4) Build titles for subplots
########################################
if target is None:
    # No reaction pattern found => use input file's first line
    # for the overall plot title
    # We'll just reuse that line on both subplots
    elastic_title = first_line_in
    reaction_title   = first_line_in
else:
    # Construct titles from reaction info
    # e.g. "Elastic: $^{14}\mathrm{N}$($^{17}\mathrm{F}$,$^{17}\mathrm{F}$)$^{14}\mathrm{N}$ @ 170.0 MeV"
    elastic_title = (f"Elastic: {target}({projectile},{projectile})"
                     f"{target} @ {beam_energy:.1f} MeV")
    # e.g. "Other:   $^{14}\mathrm{N}$($^{17}\mathrm{F}$,$^{18}\mathrm{Ne}$)$^{13}\mathrm{C}$ @ 170.0 MeV"
    reaction_title   = (f"Reaction:   {target}({projectile},{ejectile})"
                     f"{recoil} @ {beam_energy:.1f} MeV")


########################################
# 5) Print the results
########################################
print("\nElastic Scattering (with /R):")
for a, xs, r in zip(elastic_angles, elastic_cross_sections, elastic_ratios):
    print(f"Angle={a} deg, X-S={xs} mb/sr, /R={r}")

print("\nReaction Channels (no /R):")
for a, xs in zip(reaction_angles, reaction_cross_sections):
    print(f"Angle={a} deg, X-S={xs} mb/sr")
    # save to a txt file for Geant4_DSL sampling
    with open(file_name + '_angular_distribution.txt', 'a') as f:
        f.write(f"{a} {xs}\n")


########################################
# 6) Plot the results
########################################
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
# axes[0].plot(elastic_angles, elastic_ratios, color='red', linewidth=2.0)
# data points not line!
axes[0].plot(elastic_angles, elastic_ratios, color='red', marker='o', markersize=2)
axes[0].set_xlabel(r'$\theta_{cm}$ (deg)')
axes[0].set_ylabel(r'd$\sigma_{el}/d\sigma_{Ru}$')
axes[0].set_yscale('log')
axes[0].set_title(elastic_title, fontsize=19)

# Right subplot: cross section vs. angle (other channels)
axes[1].plot(reaction_angles, reaction_cross_sections,
             color='dodgerblue', linewidth=2.0)
axes[1].set_xlabel(r'$\theta_{cm}$ (deg)')
axes[1].set_ylabel(r'd$\sigma_{tr}/d\Omega$ (mb/sr)')
axes[1].set_title(reaction_title, fontsize=19)

plt.savefig(file_name + '.png')
# os.system("xdg-open " + file_name + ".png")
