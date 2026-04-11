import time
import random
import sys
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Настройка русских шрифтов
rcParams['font.family'] = 'DejaVu Sans'


def quicksort(arr, low, high):
    """Быстрая сортировка (оптимизированная)"""
    if low < high:
        # Оптимизация: выбор медианы трёх в качестве опорного элемента
        mid = (low + high) // 2
        if arr[low] > arr[mid]:
            arr[low], arr[mid] = arr[mid], arr[low]
        if arr[low] > arr[high]:
            arr[low], arr[high] = arr[high], arr[low]
        if arr[mid] > arr[high]:
            arr[mid], arr[high] = arr[high], arr[mid]
        arr[mid], arr[high - 1] = arr[high - 1], arr[mid]

        pivot = arr[high - 1]
        i = low - 1

        for j in range(low, high - 1):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high - 1] = arr[high - 1], arr[i + 1]
        pi = i + 1

        # Оптимизация: рекурсия только для меньшей части
        if pi - low < high - pi:
            quicksort(arr, low, pi - 1)
            quicksort(arr, pi + 1, high)
        else:
            quicksort(arr, pi + 1, high)
            quicksort(arr, low, pi - 1)


def mergesort(arr):
    """Сортировка слиянием"""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])

    return merge(left, right)


def merge(left, right):
    """Слияние двух отсортированных массивов"""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heapsort(arr):
    """Пирамидальная сортировка"""

    def heapify(arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)

    # Построение пирамиды
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Извлечение элементов
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)


def insertion_sort(arr):
    """Сортировка вставками (для малых массивов)"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def measure_time(sort_func, arr, *args):
    """Измерение времени выполнения с усреднением"""
    times = []

    for _ in range(5):  # 5 измерений для усреднения
        arr_copy = arr.copy()
        start = time.perf_counter()

        if sort_func.__name__ == "quicksort":
            sort_func(arr_copy, 0, len(arr_copy) - 1)
        elif sort_func.__name__ == "mergesort":
            arr_copy = sort_func(arr_copy)
        elif sort_func.__name__ == "heapsort":
            sort_func(arr_copy)
        else:
            sort_func(arr_copy)

        end = time.perf_counter()
        times.append(end - start)

    return sum(times) / len(times)


def generate_data(size, data_type):
    """Генерация тестовых данных"""
    if data_type == "random":
        return [random.randint(0, 1000000) for _ in range(size)]
    elif data_type == "sorted":
        return list(range(size))
    elif data_type == "reversed":
        return list(range(size, 0, -1))
    elif data_type == "few_unique":
        return [random.randint(0, 100) for _ in range(size)]
    return [random.randint(0, 1000000) for _ in range(size)]


def run_experiment():
    """Проведение эксперимента"""
    sizes = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    data_types = ["random", "sorted", "reversed", "few_unique"]
    algorithms = {
        "Quicksort (оптимизир.)": quicksort,
        "Mergesort": mergesort,
        "Heapsort": heapsort
    }

    results = {}

    print("ЭМПИРИЧЕСКОЕ ИССЛЕДОВАНИЕ АЛГОРИТМОВ СОРТИРОВКИ")

    for data_type in data_types:
        print(f"ТИП ДАННЫХ: {data_type.upper()}")

        results[data_type] = {}

        for algo_name, algo_func in algorithms.items():
            print(f"\nТестирование: {algo_name}")
            results[data_type][algo_name] = []

            for size in sizes:
                # Пропуск больших размеров для опасных случаев
                if data_type == "reversed" and algo_name == "Quicksort (оптимизир.)" and size > 20000:
                    print(f"  Размер {size:8d}: пропуск (риск переполнения)")
                    results[data_type][algo_name].append(None)
                    continue

                data = generate_data(size, data_type)
                time_taken = measure_time(algo_func, data)
                results[data_type][algo_name].append(time_taken)

                print(f"  Размер {size:8d}: {time_taken:.6f} сек")

    return results, sizes, data_types, algorithms


def visualize_results(results, sizes, data_types, algorithms):
    """Визуализация результатов"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    markers = ['o', 's', '^', 'D']

    for idx, data_type in enumerate(data_types):
        ax = axes[idx]

        for i, (algo_name, _) in enumerate(algorithms.items()):
            times = results[data_type][algo_name]
            valid_sizes = [s for s, t in zip(sizes, times) if t is not None]
            valid_times = [t for t in times if t is not None]

            if valid_sizes and valid_times:
                ax.plot(valid_sizes, valid_times,
                        marker=markers[i % len(markers)],
                        color=colors[i % len(colors)],
                        label=algo_name,
                        linewidth=2,
                        markersize=8)

        ax.set_xlabel("Размер массива (n)", fontsize=12)
        ax.set_ylabel("Время выполнения (секунды)", fontsize=12)
        ax.set_title(f"Тип данных: {data_type}", fontsize=14)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig("sorting_algorithms_comparison.png", dpi=150)
    plt.show()
    print("\n✅ Графики сохранены в 'sorting_algorithms_comparison.png'")


def print_summary_table(results, sizes, data_types, algorithms):
    """Вывод сводной таблицы"""
    print("\n" + "=" * 100)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ (время выполнения, секунды)")
    print("=" * 100)

    for data_type in data_types:
        print(f"\n--- {data_type.upper()} ---")
        print(f"{'Размер':>10} |", end="")
        for algo_name in algorithms.keys():
            print(f" {algo_name[:20]:>22} |", end="")
        print()
        print("-" * (40 + 25 * len(algorithms)))

        for i, size in enumerate(sizes):
            print(f"{size:10d} |", end="")
            for algo_name in algorithms.keys():
                time_val = results[data_type][algo_name][i]
                if time_val is not None:
                    print(f" {time_val:22.6f} |", end="")
                else:
                    print(f" {'N/A':>22} |", end="")
            print()


def calculate_statistics(results, data_types, algorithms):
    """Расчёт статистических характеристик"""
    print("\n" + "=" * 80)
    print("СТАТИСТИЧЕСКИЙ АНАЛИЗ")
    print("=" * 80)

    for data_type in data_types:
        print(f"\n--- {data_type.upper()} ---")

        for algo_name in algorithms.keys():
            times = [t for t in results[data_type][algo_name] if t is not None]

            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                std_dev = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5

                print(f"\n{algo_name}:")
                print(f"  Среднее время: {avg_time:.6f} сек")
                print(f"  Минимальное время: {min_time:.6f} сек")
                print(f"  Максимальное время: {max_time:.6f} сек")
                print(f"  Стандартное отклонение: {std_dev:.6f} сек")


def main():
    """Основная функция"""
    print("\n" + "=" * 80)
    print("Задача: Оптимизация алгоритма сортировки для больших массивов данных")
    print("=" * 80)

    # Проведение эксперимента
    results, sizes, data_types, algorithms = run_experiment()

    # Вывод сводной таблицы
    print_summary_table(results, sizes, data_types, algorithms)

    # Статистический анализ
    calculate_statistics(results, data_types, algorithms)

    # Визуализация
    visualize_results(results, sizes, data_types, algorithms)

    print("\n✅ Эксперимент успешно завершён!")


if __name__ == "__main__":
    main()