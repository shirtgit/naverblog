import matplotlib.pyplot as plt

from utils.colors import Colors

import matplotlib.pyplot as plt


def show_color_side_by_side(bg_color, text_color):
    fig, ax = plt.subplots(figsize=(4, 2))

    # 왼쪽: 배경색 박스
    ax.add_patch(plt.Rectangle((0, 0), 0.5, 1, color=bg_color))
    ax.text(0.25, 0.5, bg_color, ha='center', va='center', fontsize=10,
            color='white' if bg_color in ['black', 'navy', 'darkblue', 'indigo'] else 'black')

    # 오른쪽: 텍스트색 박스
    ax.add_patch(plt.Rectangle((0.5, 0), 0.5, 1, color=text_color))
    ax.text(0.75, 0.5, text_color, ha='center', va='center', fontsize=10,
            color='white' if text_color in ['black', 'navy', 'darkblue', 'indigo'] else 'black')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.show()

color = Colors()

for i in range(100):
    bg, text = color.get_color(i)  # 또는 get_color(i)
    show_color_side_by_side(bg, text)