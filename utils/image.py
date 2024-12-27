from typing import List, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import os
from dataclasses import dataclass

from utils.characters import CharacterManager

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SENSITIVE_WORDS = CharacterManager.load_name_list(
    SCRIPT_DIR / ".." / "metadata" / "common" / "sensitive_words.yml"
)

@dataclass
class TextStyle:
    """文本样式配置"""
    font_path: str
    font_size: int
    line_spacing: float = 1.0
    text_color: str = 'black'
    background_color: str = 'white'
    highlight_color: str = 'red'

class TextImageGenerator:
    """文本图像生成器"""
    def __init__(self, style: TextStyle):
        self.style = style
        self.font = ImageFont.truetype(style.font_path, style.font_size)

    def create_text_image(
        self, 
        text: str, 
        image_width: int, 
        margin: int, 
        plain: bool = False
    ) -> Image.Image:
        """将文本转换为图像"""
        # 创建绘图上下文来测量文本大小
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        # 计算所需的行数和高度
        lines = text.split('\n')
        line_height = self.font.getsize('Ay')[1] * self.style.line_spacing
        text_height = len(lines) * line_height

        # 计算图像尺寸
        image_height = math.floor(text_height + 2 * margin)
        
        # 创建图像
        img = Image.new(
            'RGB', 
            (image_width, image_height), 
            color=self.style.background_color
        )
        img.info['dpi'] = (600, 600)
        draw = ImageDraw.Draw(img)

        # 绘制文本
        sensitive_count = self._draw_text_lines(
            draw, lines, margin, line_height, plain
        )
        
        if sensitive_count > 0:
            print(f"Found {sensitive_count} sensitive words!")

        return self._remove_bottom_whitespace(img, margin * 3)

    def _draw_text_lines(
        self, 
        draw: ImageDraw.Draw, 
        lines: List[str], 
        margin: int, 
        line_height: float,
        plain: bool
    ) -> int:
        """绘制文本行"""
        sensitive_count = 0
        y = margin

        for line in lines:
            _, text_height = draw.textsize(line, font=self.font)
            words_index = [] if plain else find_sensitive_words_index(line)
            
            if not words_index:
                draw.text(
                    (margin, y), 
                    line, 
                    fill=self.style.text_color, 
                    font=self.font
                )
            else:
                sensitive_count += len(words_index)
                self._draw_line_with_highlights(
                    draw, line, words_index, margin, y, text_height
                )
                
            y += int(text_height * self.style.line_spacing)

        return sensitive_count

    def _draw_line_with_highlights(
        self,
        draw: ImageDraw.Draw,
        line: str,
        words_index: List[int],
        x: int,
        y: int,
        text_height: int
    ) -> None:
        """绘制带有高亮的文本行"""
        start = 0
        current_x = x

        for i in words_index:
            # 绘制普通文本
            if start < i:
                normal_text = line[start:i]
                draw.text(
                    (current_x, y),
                    normal_text,
                    fill=self.style.text_color,
                    font=self.font
                )
                current_x += self.font.getsize(normal_text)[0]
            
            # 绘制高亮字符
            if start == i:
                char = line[i]
                draw.text(
                    (current_x, y),
                    char,
                    fill=self.style.text_color,
                    font=self.font
                )
                char_width = self.font.getsize(char)[0]
                
                # 绘制高亮矩形
                draw.rectangle(
                    [
                        (current_x, y + text_height/3),
                        (current_x + char_width, y + text_height * 0.8)
                    ],
                    fill=self.style.highlight_color
                )
                
                current_x += char_width
                start += 1

    def _remove_bottom_whitespace(
        self, 
        img: Image.Image, 
        margin: int
    ) -> Image.Image:
        """移除图像底部的空白"""
        width, height = img.size
        data = list(img.getdata())
        
        # 从底部向上扫描，找到最后一个非空白行
        for y in range(height - 1, -1, -1):
            row_data = data[y * width:(y + 1) * width]
            if any(sum(pixel) != 255 * 3 for pixel in row_data):
                bottom = y + 1
                return img.crop((0, 0, width, bottom + margin))
        
        return img

def find_sensitive_words_index(text: str) -> List[int]:
    """查找敏感词的索引位置"""
    indexes = set()
    
    for keyword in SENSITIVE_WORDS:
        start = 0
        while True:
            index = text.find(keyword, start)
            if index == -1:
                break
            indexes.update(range(index, index + len(keyword)))
            start = index + 1
            
    return sorted(list(indexes))

def text_to_image(
    text: str,
    font_path: str,
    font_size: int,
    image_width: int,
    margin: int,
    plain: bool = False
) -> Image.Image:
    """将文本转换为图像的便捷函数"""
    style = TextStyle(
        font_path=font_path,
        font_size=font_size
    )
    generator = TextImageGenerator(style)
    return generator.create_text_image(text, image_width, margin, plain)



