import sys
import os
from database import Database
from models import StudentRepository, CourseRepository, GradeRepository


def init_database():
    """Инициализация БД: создание таблиц и загрузка тестовых данных."""
    db = Database()

    # Проверка, существует ли уже база данных
    if os.path.exists("students.db"):
        # Проверяем, есть ли данные
        result = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        if result:
            print("ℹ️ База данных уже существует")
            return

    # Создание таблиц - разбиваем скрипт на отдельные запросы
    with open("db_schema.sql", "r", encoding="utf-8") as f:
        schema_content = f.read()

    # Разделяем запросы по точке с запятой
    queries = [q.strip() for q in schema_content.split(';') if q.strip()]

    # Выполняем каждый запрос отдельно
    for query in queries:
        try:
            db.execute_query(query)
        except Exception as e:
            print(f"⚠️ Ошибка при выполнении запроса: {e}")
            print(f"Запрос: {query[:100]}...")

    # Загрузка тестовых данных, если таблица студентов пуста
    students = db.fetch_all("SELECT COUNT(*) as cnt FROM students")
    if students and students[0]["cnt"] == 0:
        with open("test_data.sql", "r", encoding="utf-8") as f:
            test_data_content = f.read()

        # Разделяем тестовые данные на отдельные запросы
        test_queries = [q.strip() for q in test_data_content.split(';') if q.strip()]

        for query in test_queries:
            try:
                db.execute_query(query)
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке тестовых данных: {e}")

        print("✅ База данных инициализирована с тестовыми данными")


def print_menu():
    """Вывод главного меню."""
    print("\n" + "=" * 50)
    print("📚 СИСТЕМА УЧЁТА ОБУЧАЮЩИХСЯ")
    print("=" * 50)
    print("1. Список всех студентов")
    print("2. Добавить нового студента")
    print("3. Удалить студента")
    print("4. Посмотреть оценки студента")
    print("5. Добавить оценку студенту")
    print("6. Топ студентов по успеваемости")
    print("7. Список курсов")
    print("8. Добавить новый курс")
    print("9. Средний балл всех студентов")
    print("0. Выход")
    print("-" * 50)


def main():
    """Основной цикл программы."""
    # Инициализация
    try:
        init_database()
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        print("Проверьте наличие файлов db_schema.sql и test_data.sql")
        return

    db = Database()
    student_repo = StudentRepository(db)
    course_repo = CourseRepository(db)
    grade_repo = GradeRepository(db)

    while True:
        try:
            print_menu()
            choice = input("Выберите действие: ").strip()

            if choice == "1":
                # Список студентов
                students = student_repo.get_all_students()
                if not students:
                    print("📭 Нет студентов в базе")
                else:
                    print("\n📋 СПИСОК СТУДЕНТОВ:")
                    print("-" * 60)
                    for s in students:
                        print(f"  {s['id']:2d}. {s['last_name']:15} {s['first_name']:12} | {s['email']}")
                    print("-" * 60)

            elif choice == "2":
                # Добавление студента
                print("\n➕ ДОБАВЛЕНИЕ СТУДЕНТА")
                first = input("Имя: ").strip()
                last = input("Фамилия: ").strip()
                birth = input("Дата рождения (ГГГГ-ММ-ДД, можно пропустить): ").strip()
                email = input("Email: ").strip()

                if first and last and email:
                    try:
                        student_repo.add_student(first, last, birth if birth else None, email)
                        print("✅ Студент добавлен")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                else:
                    print("❌ Имя, фамилия и email обязательны")

            elif choice == "3":
                # Удаление студента
                student_id = input("Введите ID студента для удаления: ").strip()
                if student_id.isdigit():
                    # Проверяем, существует ли студент
                    student = student_repo.get_student_by_id(int(student_id))
                    if student:
                        student_repo.delete_student(int(student_id))
                        print("✅ Студент удалён")
                    else:
                        print("❌ Студент с таким ID не найден")
                else:
                    print("❌ Некорректный ID")

            elif choice == "4":
                # Просмотр оценок студента
                student_id = input("Введите ID студента: ").strip()
                if student_id.isdigit():
                    student = student_repo.get_student_by_id(int(student_id))
                    if not student:
                        print("❌ Студент не найден")
                        continue

                    print(f"\n📊 СТУДЕНТ: {student['last_name']} {student['first_name']}")
                    grades = grade_repo.get_student_grades(int(student_id))
                    avg = grade_repo.get_average_grade_for_student(int(student_id))

                    if grades:
                        print(f"Средний балл: {avg:.2f}")
                        print("\nОЦЕНКИ:")
                        print("-" * 40)
                        for g in grades:
                            print(f"  {g['title']:20} : {g['grade']}  ({g['date_received']})")
                        print("-" * 40)
                    else:
                        print("📭 У студента пока нет оценок")
                else:
                    print("❌ Некорректный ID")

            elif choice == "5":
                # Добавление оценки
                student_id = input("ID студента: ").strip()
                if not student_id.isdigit():
                    print("❌ Некорректный ID")
                    continue

                # Проверяем существование студента
                student = student_repo.get_student_by_id(int(student_id))
                if not student:
                    print("❌ Студент не найден")
                    continue

                courses = course_repo.get_all_courses()
                if not courses:
                    print("❌ Нет доступных курсов. Сначала добавьте курсы.")
                    continue

                print(f"\nСтудент: {student['last_name']} {student['first_name']}")
                print("\nДоступные курсы:")
                for c in courses:
                    print(f"  {c['id']:2d}. {c['title']:25} (кредитов: {c['credits']})")

                course_id = input("\nID курса: ").strip()
                grade = input("Оценка (2-5): ").strip()

                if course_id.isdigit() and grade.isdigit() and 2 <= int(grade) <= 5:
                    try:
                        grade_repo.add_grade(int(student_id), int(course_id), int(grade))
                        print("✅ Оценка добавлена")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                else:
                    print("❌ Некорректные данные. Оценка должна быть от 2 до 5")

            elif choice == "6":
                # Топ студентов
                limit = input("Сколько студентов показать (по умолчанию 3): ").strip()
                limit = int(limit) if limit.isdigit() else 3
                top = grade_repo.get_top_students(limit)

                if top:
                    print(f"\n🏆 ТОП-{limit} СТУДЕНТОВ ПО УСПЕВАЕМОСТИ:")
                    print("-" * 50)
                    for i, s in enumerate(top, 1):
                        print(f"  {i}. {s['last_name']:15} {s['first_name']:12} — средний балл: {s['avg_grade']:.2f}")
                    print("-" * 50)
                else:
                    print("📭 Нет данных об успеваемости")

            elif choice == "7":
                # Список курсов
                courses = course_repo.get_all_courses()
                if courses:
                    print("\n📚 СПИСОК КУРСОВ:")
                    print("-" * 50)
                    for c in courses:
                        print(f"  {c['id']:2d}. {c['title']:30} (кредитов: {c['credits']})")
                    print("-" * 50)
                else:
                    print("📭 Нет курсов в базе")

            elif choice == "8":
                # Добавление нового курса
                print("\n➕ ДОБАВЛЕНИЕ КУРСА")
                title = input("Название курса: ").strip()
                credits = input("Количество кредитов (по умолчанию 3): ").strip()

                if title:
                    credits = int(credits) if credits.isdigit() else 3
                    try:
                        course_repo.add_course(title, credits)
                        print("✅ Курс добавлен")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                else:
                    print("❌ Название курса обязательно")

            elif choice == "9":
                # Средний балл всех студентов
                students = student_repo.get_all_students()
                if not students:
                    print("📭 Нет студентов в базе")
                    continue

                print("\n📊 СРЕДНИЙ БАЛЛ СТУДЕНТОВ:")
                print("-" * 50)
                for s in students:
                    avg = grade_repo.get_average_grade_for_student(s['id'])
                    if avg > 0:
                        print(f"  {s['last_name']:15} {s['first_name']:12} — {avg:.2f}")
                    else:
                        print(f"  {s['last_name']:15} {s['first_name']:12} — нет оценок")
                print("-" * 50)

            elif choice == "0":
                print("\n👋 До свидания!")
                sys.exit(0)

            else:
                print("❌ Неверный выбор, попробуйте снова")

        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            print("Попробуйте снова или перезапустите программу")


if __name__ == "__main__":
    main()