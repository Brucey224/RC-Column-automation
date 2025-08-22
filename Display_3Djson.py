import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns

# Load JSON
with open("cover_lookup.json") as f:
    data = json.load(f)

# Ordered axes
cements = ["CEM I","CEM II/A","CEM II/B-S","SRPC","CEM II/B-V","CEM III/A","CEM III/B","CEM IV/B"]
grades = ["C12/16","C16/20","C20/25","C25/30","C28/35","C30/37","C32/40","C35/45",
          "C40/50","C45/55","C50/60","C55/67","C60/75","C70/85","C80/95","C90/105"]
exposures = list(data.keys())

def plot_heatmap_for_exposure(exposure):
    # Build matrix of cover values
    matrix = []
    for grade in grades:
        row = []
        for cement in cements:
            cover = data.get(exposure, {}).get(cement, {}).get(grade, {}).get("cover", None)
            row.append(np.nan if cover is None else cover)
        matrix.append(row)

    matrix = np.array(matrix)

    # Define custom colormap: black for NaN
    cmap = sns.color_palette("coolwarm", as_cmap=True)
    sns.set(style="whitegrid")

    plt.figure(figsize=(10, 6))
    sns.heatmap(matrix,
                cmap=cmap,
                annot=True,
                fmt=".0f",
                xticklabels=cements,
                yticklabels=grades,
                linewidths=0.5,
                cbar_kws={'label': 'Cover (mm)'},
                mask=np.isnan(matrix))  # mask NaN → draws them separately

    # Overplot NaN cells in black
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isnan(matrix[i, j]):
                plt.gca().add_patch(plt.Rectangle((j, i), 1, 1, fill=True, color="black", ec="white", lw=0.5))

    plt.title(f"Heatmap of Cover for Exposure {exposure}")
    plt.xlabel("Cement Type")
    plt.ylabel("Concrete Grade")
    plt.tight_layout()
    plt.show()

exposures = list(data.keys())

def plot_3d_cover_blocks():
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Prepare data
    xs, ys, zs, covers = [], [], [], []
    for z, exposure in enumerate(exposures):
        for y, grade in enumerate(grades):
            for x, cement in enumerate(cements):
                cover = data.get(exposure, {}).get(cement, {}).get(grade, {}).get("cover", None)
                if cover is not None:
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
                    covers.append(cover)

    # Normalize cover values for colormap
    covers_arr = np.array(covers)
    norm = plt.Normalize(covers_arr.min(), covers_arr.max())
    colors = cm.coolwarm(norm(covers_arr))

    # "Explode" blocks: raise them above the base
    dz = np.full_like(xs, 0.8)  # block height
    ax.bar3d(xs, ys, zs, 0.8, 0.8, dz, color=colors, edgecolor='k', shade=True)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(cements)) + 0.4)
    ax.set_xticklabels(cements, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(grades)) + 0.4)
    ax.set_yticklabels(grades)
    ax.set_zticks(np.arange(len(exposures)) + 0.4)
    ax.set_zticklabels(exposures)
    ax.set_xlabel('Cement Type')
    ax.set_ylabel('Concrete Grade')
    ax.set_zlabel('Exposure Class')

    # Colorbar
    mappable = cm.ScalarMappable(norm=norm, cmap=cm.coolwarm)
    mappable.set_array(covers_arr)
    cbar = plt.colorbar(mappable, ax=ax, pad=0.1, shrink=0.7)
    cbar.set_label('Cover (mm)')

    plt.title("3D Cover Block Plot (Exploded by Value)")
    plt.tight_layout()
    plt.show()

plot_3d_cover_blocks()

# Example: plot one exposure class
plot_heatmap_for_exposure("XC1")
