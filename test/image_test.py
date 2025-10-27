import colorsys
import random
import time

from PIL import ImageColor
import platform
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, ColorClip, CompositeVideoClip

from utils.colors import Colors
from media import image

FONT_SIZE = 60

# 기존 사진에 테두리 입히기
#   - 테두리 색: 썸네일 이미지 생성 시 사용하는 색 활용 (일단 빨간색으로 테스트)
#   - 테두리 굵기: 범위 내에서 랜덤으로 조절 (굵기 = 3으로 테스트)
def test_border_sample():
    global image_path
    image.draw_border_sample(image_path)

# 기존 사진 명도, 채도 랜덤으로 조절


# 썸네일 사진 생성
#   - 색 조합 50-100가지
#   - 명도, 채도 랜덤으로 조절
#   - 테두리 입히기
def test_generate_thumbnail():
    image.generate_image("010-9872-1349", "성수동 설비업체")

# root_dir = os.path.dirname(os.path.abspath(__file__))
# image_path = os.path.join(root_dir, "..", "sample", "sample1.jpg")
# test_border_sample()

# 색 대비 파악 - 100개 모두 출력
def get_korean_font(size=24):
    try:
        system = platform.system()
        if system == "Windows":
            return ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size)
        elif system == "Darwin":
            return ImageFont.truetype("/System/Library/Fonts/AppleGothic.ttf", size)
        else:
            return ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", size)
    except IOError:
        return ImageFont.load_default()

def draw_bold_text(draw, position, text, font, fill, boldness=1.5):
    x, y = position
    offsets = [(0, 0)]
    i = 0.5
    while i <= boldness:
        offsets.extend([(i, 0), (0, i), (i, i)])
        i += 0.5
    for ox, oy in offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=fill)

def draw_border_thumbnail(draw, width, height, thickness=3, color="red"):
    for i in range(thickness):
        draw.rectangle(
            [i, i, width - i - 1, height - i - 1],
            outline=color
        )

def get_luminance(rgb):
    srgb = [c / 255.0 for c in rgb]

    def linearize(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = map(linearize, srgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def get_contrast_ratio(rgb1, rgb2):
    l1 = get_luminance(rgb1)
    l2 = get_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def adjust_color_preserving_contrast(fg_color_name, bg_color_name, lightness_shift=0.08, saturation_shift=0.1, min_contrast=4.5):
    fg_rgb_orig = ImageColor.getrgb(fg_color_name)
    bg_rgb_orig = ImageColor.getrgb(bg_color_name)

    h, l, s = colorsys.rgb_to_hls(*[c / 255.0 for c in fg_rgb_orig])

    # 랜덤 조정
    l_new = min(max(l + random.uniform(-lightness_shift, lightness_shift), 0), 1)
    s_new = min(max(s + random.uniform(-saturation_shift, saturation_shift), 0), 1)

    r2, g2, b2 = colorsys.hls_to_rgb(h, l_new, s_new)
    fg_rgb_adj = tuple(int(c * 255) for c in (r2, g2, b2))

    # 대비 유지 확인
    contrast = get_contrast_ratio(fg_rgb_adj, bg_rgb_orig)
    original_contrast = get_contrast_ratio(fg_rgb_orig, bg_rgb_orig)

    if contrast >= min_contrast and contrast >= original_contrast * 0.9:  # 원래 대비의 90% 이상 유지
        return fg_rgb_adj, bg_rgb_orig
    else:
        return fg_rgb_orig, bg_rgb_orig  # 조정 실패 → 원본 반환

def generate_image(phone, address, company):
    colors = Colors()
    length = colors.get_color_length()
    print(length)
    for index in range(length):
        # bg_color, text_color = colors.get_color(i)
        # width, height = 400, 400
        # thumbnail = Image.new('RGB', (width, height), bg_color)
        # draw = ImageDraw.Draw(thumbnail)

        text_color, bg_color = colors.get_color(index)
        text_revised, bg_revised = adjust_color_preserving_contrast(text_color, bg_color)

        width, height = 400, 400
        thumbnail = Image.new('RGB', (width, height), bg_revised)
        draw = ImageDraw.Draw(thumbnail)

        # 수정
        company_elements = [c.strip() for c in company.split(" ")]

        print(company_elements)

        line_data = [
            (phone, 45),
            (address, FONT_SIZE),
            (company_elements[0], FONT_SIZE),
        ]

        # 수정
        if len(company_elements) == 2:
            line_data.append((company_elements[1], FONT_SIZE))

        total_text_height = 0
        line_spacing = 20  # 수정
        line_heights = []

        for text, font_size in line_data:
            line_heights.append((font_size, line_spacing))
            total_text_height += font_size + line_spacing

        total_text_height -= line_heights[-1][1]  # ✅ (수정) 마지막 줄은 spacing 없음
        start_y = (height - total_text_height) // 2

        # ✅ (수정) 각 줄의 폰트를 따로 불러와 개별 적용
        for i, (text, font_size) in enumerate(line_data):
            font = get_korean_font(font_size)  # ✅ (수정) 줄마다 폰트 크기 적용
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            if i == 0:
                draw_bold_text(draw, (x, start_y), text, font, fill=text_revised, boldness=3.0)
            else:
                draw_bold_text(draw, (x, start_y), text, font, fill=text_revised, boldness=2.0)

            _, line_spacing = line_heights[i]
            start_y += font_size + line_spacing

        draw_border_thumbnail(draw, width, height, thickness=3, color=text_color)
        thumbnail.save(f"../thumbnail/thumbnail{index}.png")

def generate_image_for_video(phone, company):
    colors = Colors()
    bg_color, text_color = colors.get_color(0)
    width, height = 300, 300
    thumbnail = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(thumbnail)

    font_size = 35
    line_spacing = int(font_size * 1.5)
    font = get_korean_font(font_size)
    lines = [phone, company]

    # ✅ 수정된 전체 텍스트 높이 계산
    total_text_height = font_size * len(lines) + line_spacing * (len(lines) - 1)
    start_y = (height - total_text_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw_bold_text(draw, (x, start_y), line, font, fill=text_color, boldness=0.5)
        start_y += font_size + line_spacing

    draw_border_thumbnail(draw, width, height, thickness=3, color=text_color)
    thumbnail.save("thumbnail.png")

def generate_video():
    video_width, video_height = 800, 400

    background = ColorClip(size=(video_width, video_height), color=(255, 255, 255)).with_duration(10)

    # 1. 이미지 파일을 불러옴
    image_clip = ImageClip(f"../thumbnail/thumbnail0.png")

    # 4. 이미지 위치 중앙 정렬
    image_clip = image_clip.with_position(("center", "center"))

    # 5. 합성
    final_clip = CompositeVideoClip([background, image_clip])

    # 6. 영상으로 저장
    final_clip.write_videofile("output.mov", fps=24)
    final_clip.duration = 10

# generate_image_for_video("010-9872-1349", "성수동 설비업체")
generate_image("010-4119-2101", "성수동", "설비업체")
time.sleep(10)
generate_video()