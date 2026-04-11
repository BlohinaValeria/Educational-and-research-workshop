#!/usr/bin/env python3
"""
Лабораторная работа №3
Сравнение сжатия PNG и WebP Lossless
"""

import os
import time
import hashlib
from PIL import Image
import numpy as np

# Конфигурация
PNG_LEVEL = 9
WEBP_LEVEL = 6
REPEATS = 3  # Для пилота можно 3 повтора

# Попробуем импортировать memory_profiler, но если его нет - работаем без него
try:
    from memory_profiler import memory_usage

    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    print("⚠️ memory_profiler не установлен. Замер памяти будет пропущен.")
    print("   Установите: pip install memory-profiler")


def create_test_images():
    """Создаёт тестовые BMP-изображения, если их нет"""
    os.makedirs('test_images', exist_ok=True)

    test_images_config = [
        ('photo1.bmp', (1920, 1080), 'gradient'),
        ('screenshot1.bmp', (1366, 768), 'blocks'),
        ('icon1.bmp', (256, 256), 'checkerboard'),
        ('graph1.bmp', (800, 600), 'gradient'),
        ('text1.bmp', (1920, 1080), 'blocks'),
    ]

    for filename, size, pattern in test_images_config:
        filepath = os.path.join('test_images', filename)

        if os.path.exists(filepath):
            print(f"Файл уже существует: {filepath}")
            continue

        print(f"Создаю: {filepath} ({size[0]}x{size[1]}, {pattern})")

        if pattern == 'gradient':
            img_data = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            for x in range(size[0]):
                img_data[:, x, 0] = int(255 * x / size[0])
                img_data[:, x, 1] = int(255 * (1 - x / size[0]))
        elif pattern == 'blocks':
            img_data = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            block_w, block_h = max(1, size[0] // 8), max(1, size[1] // 8)
            for i in range(8):
                for j in range(8):
                    color = ((i * 32) % 256, (j * 32) % 256, ((i + j) * 16) % 256)
                    y_start, y_end = j * block_h, min((j + 1) * block_h, size[1])
                    x_start, x_end = i * block_w, min((i + 1) * block_w, size[0])
                    img_data[y_start:y_end, x_start:x_end] = color
        else:  # checkerboard
            img_data = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            tile = 32
            for y in range(size[1]):
                for x in range(size[0]):
                    if ((x // tile) + (y // tile)) % 2 == 0:
                        img_data[y, x] = [255, 255, 255]
                    else:
                        img_data[y, x] = [100, 100, 100]

        img = Image.fromarray(img_data, mode='RGB')
        img.save(filepath, 'BMP')
        print(f"  ✅ Создано: {os.path.getsize(filepath)} байт")


def compress_png(input_path, output_path):
    """Сжатие в PNG с замером времени"""
    img = Image.open(input_path)

    start = time.perf_counter()
    img.save(output_path, 'PNG', compress_level=PNG_LEVEL)
    elapsed = (time.perf_counter() - start) * 1000

    # Замер памяти (если доступен)
    mem = 0
    if HAS_MEMORY_PROFILER:
        try:
            mem_usage = memory_usage(
                (img.save, (output_path + '_tmp.png',), {'format': 'PNG', 'compress_level': PNG_LEVEL}), interval=0.01,
                max_usage=True)
            if mem_usage and isinstance(mem_usage, list):
                mem = max(mem_usage)
            elif isinstance(mem_usage, (int, float)):
                mem = mem_usage
        except:
            mem = 0

    return elapsed, mem


def compress_webp(input_path, output_path):
    """Сжатие в WebP Lossless с замером времени"""
    img = Image.open(input_path)

    start = time.perf_counter()
    img.save(output_path, 'WEBP', lossless=True, quality=WEBP_LEVEL)
    elapsed = (time.perf_counter() - start) * 1000

    # Замер памяти (если доступен)
    mem = 0
    if HAS_MEMORY_PROFILER:
        try:
            mem_usage = memory_usage(
                (img.save, (output_path + '_tmp.webp',), {'format': 'WEBP', 'lossless': True, 'quality': WEBP_LEVEL}),
                interval=0.01, max_usage=True)
            if mem_usage and isinstance(mem_usage, list):
                mem = max(mem_usage)
            elif isinstance(mem_usage, (int, float)):
                mem = mem_usage
        except:
            mem = 0

    return elapsed, mem


def verify_lossless(original_path, decoded_path):
    """Проверка идентичности изображений"""
    try:
        orig = np.array(Image.open(original_path))
        dec = np.array(Image.open(decoded_path))

        if orig.shape != dec.shape:
            return False, f"Размеры не совпадают: {orig.shape} vs {dec.shape}"

        diff = np.abs(orig.astype(np.int16) - dec.astype(np.int16))
        max_diff = np.max(diff)

        if max_diff == 0:
            return True, "✅ Изображения идентичны"
        else:
            return False, f"❌ Различия в пикселях: max={max_diff}"
    except Exception as e:
        return False, str(e)


def run_experiment(image_files):
    """Запуск полного эксперимента"""
    results = []

    for img_path in image_files:
        # Нормализация пути (для Windows)
        img_path = img_path.replace('/', os.sep)

        if not os.path.exists(img_path):
            print(f"❌ Файл не найден: {img_path}")
            continue

        print(f"\n📷 Обработка: {img_path}")
        print(f"   Размер файла: {os.path.getsize(img_path) / 1024:.1f} КБ")

        png_times = []
        webp_times = []
        png_sizes = []
        webp_sizes = []
        png_mem = []
        webp_mem = []

        for repeat in range(REPEATS):
            print(f"   Повтор {repeat + 1}/{REPEATS}...")

            # PNG
            png_path = img_path.replace('.bmp', f'_test_{repeat}.png')
            t_png, mem_png = compress_png(img_path, png_path)
            png_times.append(t_png)
            png_sizes.append(os.path.getsize(png_path))
            png_mem.append(mem_png)

            # WebP
            webp_path = img_path.replace('.bmp', f'_test_{repeat}.webp')
            t_webp, mem_webp = compress_webp(img_path, webp_path)
            webp_times.append(t_webp)
            webp_sizes.append(os.path.getsize(webp_path))
            webp_mem.append(mem_webp)

            # Проверка корректности (только для первого повтора)
            if repeat == 0:
                print(f"      Проверка PNG: {verify_lossless(img_path, png_path)[1]}")
                print(f"      Проверка WebP: {verify_lossless(img_path, webp_path)[1]}")

        results.append({
            'file': os.path.basename(img_path),
            'original_size': os.path.getsize(img_path),
            'png_size': sum(png_sizes) / len(png_sizes),
            'webp_size': sum(webp_sizes) / len(webp_sizes),
            'png_time': sum(png_times) / len(png_times),
            'webp_time': sum(webp_times) / len(webp_times),
            'png_mem': sum(png_mem) / len(png_mem) if any(png_mem) else 0,
            'webp_mem': sum(webp_mem) / len(webp_mem) if any(webp_mem) else 0,
            'png_ratio': os.path.getsize(img_path) / (sum(png_sizes) / len(png_sizes)),
            'webp_ratio': os.path.getsize(img_path) / (sum(webp_sizes) / len(webp_sizes))
        })

        # Очистка временных файлов (опционально - закомментируйте, если хотите сохранить)
        for repeat in range(REPEATS):
            png_path = img_path.replace('.bmp', f'_test_{repeat}.png')
            webp_path = img_path.replace('.bmp', f'_test_{repeat}.webp')
            if os.path.exists(png_path):
                os.remove(png_path)
            if os.path.exists(webp_path):
                os.remove(webp_path)

    return results


def print_results(results):
    """Вывод результатов в красивой таблице"""
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТА")
    print("=" * 80)

    # Заголовок таблицы
    print(f"\n{'Изображение':<20} {'Исходный':<12} {'PNG':<20} {'WebP':<20} {'Экономия':<10}")
    print(f"{'':<20} {'размер, КБ':<12} {'размер, КБ | время, мс':<20} {'размер, КБ | время, мс':<20} {'':<10}")
    print("-" * 80)

    for r in results:
        name = r['file'][:18]
        orig = r['original_size'] / 1024
        png_size = r['png_size'] / 1024
        webp_size = r['webp_size'] / 1024
        saving = (1 - webp_size / png_size) * 100 if png_size > 0 else 0

        print(
            f"{name:<20} {orig:<12.1f} {png_size:<8.1f} | {r['png_time']:<6.2f}   {webp_size:<8.1f} | {r['webp_time']:<6.2f}   {saving:>5.1f}%")

    print("-" * 80)

    # Общая статистика
    if results:
        avg_png_ratio = sum(r['png_ratio'] for r in results) / len(results)
        avg_webp_ratio = sum(r['webp_ratio'] for r in results) / len(results)
        avg_png_time = sum(r['png_time'] for r in results) / len(results)
        avg_webp_time = sum(r['webp_time'] for r in results) / len(results)
        avg_saving = sum((1 - r['webp_size'] / r['png_size']) * 100 for r in results) / len(results)

        print(f"\n📊 СРЕДНИЕ ЗНАЧЕНИЯ:")
        print(f"   Коэффициент сжатия PNG:  {avg_png_ratio:.2f}")
        print(f"   Коэффициент сжатия WebP: {avg_webp_ratio:.2f}")
        print(f"   Улучшение WebP:          {(avg_webp_ratio / avg_png_ratio - 1) * 100:+.1f}%")
        print(f"   Экономия места (WebP vs PNG): {avg_saving:+.1f}%")
        print(f"   Среднее время PNG:  {avg_png_time:.2f} мс")
        print(f"   Среднее время WebP: {avg_webp_time:.2f} мс")
        print(f"   Разница по времени: {(avg_webp_time / avg_png_time - 1) * 100:+.1f}%")


# ========== ОСНОВНАЯ ПРОГРАММА ==========

if __name__ == '__main__':
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №3")
    print("Сравнение сжатия PNG vs WebP Lossless")
    print("=" * 60)

    # Шаг 1: Создаём тестовые изображения
    print("\n📁 ШАГ 1: СОЗДАНИЕ ТЕСТОВЫХ ИЗОБРАЖЕНИЙ")
    print("-" * 60)
    create_test_images()

    # Шаг 2: Запускаем эксперимент
    print("\n🔬 ШАГ 2: ЗАПУСК ЭКСПЕРИМЕНТА")
    print("-" * 60)

    test_images = [
        'test_images/photo1.bmp',
        'test_images/screenshot1.bmp',
        'test_images/icon1.bmp',
        'test_images/graph1.bmp',
        'test_images/text1.bmp',
    ]

    results = run_experiment(test_images)

    # Шаг 3: Выводим результаты
    print_results(results)

    print("\n" + "=" * 60)
    print("ЭКСПЕРИМЕНТ ЗАВЕРШЁН")
    print("=" * 60)