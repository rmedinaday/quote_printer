#! venv/bin/python

import argparse
import math
import os, os.path
import sys
from PIL import Image, ImageDraw, ImageFont

OFFSET = 10

def setupOutputDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not os.path.isdir(dir): 
        print(f'File exists and is not a directory: {dir}')
        sys.exit(3)
    if not os.access(dir, os.W_OK):
        print(f'Could not access directory: {dir}')
        sys.exit(4)
        
def getFontList(fontDir):
    fonts = []
    for i in os.listdir(fontDir):
        if i.endswith(".ttf"):
            fonts.append(i.removesuffix('.ttf'))
    return fonts

def getFont(fontDir, font):
    fontFile = os.path.join(fontDir, font + ".ttf")
    if not os.access(fontFile, os.R_OK):
        raise NameError(f'Could not find font {font}')
    return fontFile

def getWidth(font, fontSize, text):
    size = fontSize + 2 * OFFSET
    testImg = Image.new('1', (size, size), color=1)
    testDraw = ImageDraw.Draw(testImg)
    testDraw.font = font
    testDraw.fontmode = '1'
    return round(testDraw.textlength(text) + 2 * OFFSET)

def createImage(font, fontSize, text, antialias):
    imgWidth = getWidth(font, fontSize, text)    
    imgHeight = fontSize + 2 * OFFSET
    img = Image.new('1', (imgWidth, imgHeight), color=1)
    draw = ImageDraw.Draw(img)
    draw.font = font
    draw.fontmode = 'L' if antialias else '1'
    draw.text((OFFSET, OFFSET), text, fill='black')
    return img

def parse_cmdline():
    parser = argparse.ArgumentParser(
         prog='txt2img.py',
         description='Create an image from text message')
    parser.add_argument('-t', '--text', default='Hello World!',
                        help='text to use (default: %(default)s)')
    parser.add_argument('-f', '--font', default='DavidLibre-Regular',
                        help='font to use (default: %(default)s)')
    parser.add_argument('-F', '--font-dir', default='./fonts',
                        help='font directory (default: %(default)s)')
    parser.add_argument('-s', '--font-size', default=40, type=int,
                        help='font size (default: %(default)s)')
    parser.add_argument('-i', '--input', help='input file')
    parser.add_argument('-P', '--prefix', default='sample_', 
                        help='output file prefix (default: %(default)s')
    parser.add_argument('-d', '--output-dir', default='./images',
                        help='output directory (default: %(default)s)')
    parser.add_argument('-l', '--list-fonts', action='store_true', help='list available fonts')
    parser.add_argument('-a', '--antialias', action='store_true', help='font antialiasing')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_cmdline()
    if args.list_fonts:
        print(f'Available fonts:')
        for i in getFontList(args.font_dir):
            print(f'  {i}')
        sys.exit(0)
    setupOutputDir(args.output_dir)

    fontFile = getFont(args.font_dir, args.font)
    font = ImageFont.truetype(fontFile, args.font_size)
    imgHeight = args.font_size + 2 * OFFSET

    if args.input and os.access(args.input, os.R_OK):
        with open(args.input, "r") as f:
            num_lines = sum(1 for _ in f)
        padding = round(math.log10((num_lines) + 1)) + 1
        counter = 1
        with open(args.input, 'r') as f:
            for line in f:
                img = createImage(font, args.font_size, line.replace('"', '').strip(), args.antialias)
                filename = '{pfx}{ctr:0{pad}}.png'.format(pfx=args.prefix, ctr=counter, pad=padding)
                img.save(os.path.join(args.output_dir, filename))
                counter += 1
    else:
        img = createImage(font, args.font_size, args.text, args.antialias)
        filename = '{pfx}01.png'.format(pfx=args.prefix) 
        img.save(os.path.join(args.output_dir, filename))
