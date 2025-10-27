import os

import platform
import subprocess
import time
import io

from selenium.webdriver import ActionChains, Keys
import colorsys
import random

if platform.system() == "Windows":
	import win32clipboard
	import win32con

from utils import colors
from utils.decorators import sleep_after
from web import webdriver
from PIL import Image, ImageDraw, ImageFont, ImageColor
from utils.colors import Colors

from data.const import *

COMMAND_CONTROL = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

FONT_SIZE = 60

# 시각 자료 넣기
@sleep_after(1)
def upload_image(image_path):
	actions = ActionChains(webdriver.driver)
	copy_image_to_clipboard(image_path)
	time.sleep(1)
	# 윈도우면 Keys.CONTROL
	actions.key_down(COMMAND_CONTROL).send_keys('v').key_up(COMMAND_CONTROL).perform()

@sleep_after()
def copy_image_to_clipboard(image_path):
	system = platform.system()

	if system == "Darwin":  # macOS
		script = f'''
			set imgFile to POSIX file "{image_path}" as alias
			set the clipboard to (read imgFile as JPEG picture)
			'''
		result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
		if result.returncode != 0:
			print(f"Clipboard error: {result.stderr}")
		else:
			print("Clipboard updated.")
		time.sleep(1)  # 클립보드 반영 시간 확보
	elif system == "Windows":
		image = Image.open(image_path)

		# BMP로 변환 (CF_DIB를 위해)
		output = io.BytesIO()
		image.convert("RGB").save(output, "BMP")
		data = output.getvalue()[14:]  # BMP 헤더 14바이트 제거
		output.close()

		for _ in range(10):
			try:
				# 클립보드에 복사
				win32clipboard.OpenClipboard()
				win32clipboard.EmptyClipboard()
				win32clipboard.SetClipboardData(win32con.CF_DIB, data)
				win32clipboard.CloseClipboard()
				print("Clipboard updated.")
				return
			except Exception:
				time.sleep(1)
		time.sleep(1)
	else:
		raise NotImplementedError("Unsupported OS")


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

def generate_image(phone, address, company):
	colors = Colors()
	text_color, bg_color = colors.get_random_colors()
	text_revised, bg_revised = adjust_color_preserving_contrast(text_color, bg_color)

	width, height = 400, 400
	image = Image.new('RGB', (width, height), bg_revised)
	draw = ImageDraw.Draw(image)

	# 수정
	company_elements = [c.strip() for c in company.split(" ")]

	line_data = [
		(phone, 50),
		(address, FONT_SIZE),
		(company_elements[0], FONT_SIZE),
	]

	# 수정
	if len(company_elements) == 2:
		line_data.append((company_elements[1], FONT_SIZE))

	total_text_height = 0
	line_spacing = 40 # 수정
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

	# font_size = 40
	# line_spacing = int(font_size * 1.5)
	# font = get_korean_font(font_size)
	# lines = [phone, address, company]

	# ✅ 수정된 전체 텍스트 높이 계산
	# total_text_height = font_size * len(lines) + line_spacing * (len(lines) - 1)
	# start_y = (height - total_text_height) // 2
	#
	# for line in lines:
	#     bbox = draw.textbbox((0, 0), line, font=font)
	#     text_width = bbox[2] - bbox[0]
	#     x = (width - text_width) // 2
	#     draw_bold_text(draw, (x, start_y), line, font, fill=text_revised, boldness=0.5)
	#     start_y += font_size + line_spacing

	draw_border_thumbnail(draw, width, height, thickness=5, color=text_revised)
	image.save(THUMBNAIL_PATH)

def draw_border_sample(image_path):
	image = Image.open(image_path)
	draw = ImageDraw.Draw(image)
	width, height = image.size

	# 가장 짧은 변을 기준으로 비례 두께 계산 (5% ~ 10%)
	min_dimension = min(width, height)
	thickness_percent = random.uniform(0.01, 0.03)  # 5% ~ 10% 사이 랜덤
	random_thickness = int(min_dimension * thickness_percent)

	# 테두리 색상 설정
	random_color = colors.Colors().get_one_random_color()

	# 테두리 그리기
	for i in range(random_thickness):
		draw.rectangle(
			[i, i, width - i - 1, height - i - 1],
			outline=random_color
		)

	image.save(NEW_IMAGE_PATH)
	# random_thickness = random.randint(1, 5)
	# random_color = colors.Colors().get_one_random_color()
	#
	# image = Image.open(image_path)
	# draw = ImageDraw.Draw(image)
	# width, height = image.size
	#
	# i = 0
	# while i < random_thickness:
	#     draw.rectangle(
	#             [i, i, width - i - 1, height - i - 1],
	#             outline=random_color
	#         )
	#     i += 0.5
	# image.save(NEW_IMAGE_PATH)

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

def remove_image(image_path):
	os.remove(image_path)

def blog_upload_image_error():
	try:
		webdriver.click_element_xpath_error("/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button")
	except:
		pass

def cafe_upload_image_error():
	try:
		webdriver.click_element_xpath_error("/html/body/div[1]/div/div/section/div/div[2]/div[1]/div[3]/div/div[1]/div/div[3]/div[2]/div[3]/button")
	except:
		pass