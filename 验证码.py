from PIL import Image
import pytesseract
'''
只适用于最简单的验证码
RGB图 -> 灰度图 -> 二值图
图片去噪 
识别图片的数字
'''


def type_trans(path):
    img = Image.open(path)
    img = img.convert('L')
    img = img.point(get_bin_table(), '1')
    return img


def get_bin_table(threshold=140):
    table = []
    for i in range(256):
        table.append(0) if i < threshold else table.append(1)
    return table


def cut_noise(img):
    width, height = img.size
    await_change = []
    for i in range(1, width-1):
        for j in range(1, height-1):
            pixel_set = []
            for m in range(i-1, i+2):
                for n in range(j-1, j+2):
                    if img.getpixel((m, n)) == 0:
                        pixel_set.append(img.getpixel((m, n)))
            if len(pixel_set) <= 2:
                await_change.append((i, j))
    for item in await_change:
        img.putpixel(item, 1)
    return img


def main(path):
    img = type_trans(path)
    img = cut_noise(img)
    text = pytesseract.image_to_string(img, config='digits')
    text = extract_char(text)
    return text


def extract_char(text):
    exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
    text = ''.join([x for x in text if x not in exclude_char_list])
    return text


if __name__ == '__main__':
    path = 'test.png'
    text = main(path)

