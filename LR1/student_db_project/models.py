from database import Database


class StudentRepository:
    """Репозиторий для работы со студентами."""

    def __init__(self, db: Database):
        self.db = db

    def add_student(self, first_name, last_name, birth_date, email):
        """Добавление нового студента."""
        query = """
            INSERT INTO students (first_name, last_name, birth_date, email)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (first_name, last_name, birth_date, email))

    def get_all_students(self):
        """Получение списка всех студентов."""
        query = "SELECT * FROM students ORDER BY last_name"
        return self.db.fetch_all(query)

    def get_student_by_id(self, student_id):
        """Получение студента по ID."""
        query = "SELECT * FROM students WHERE id = ?"
        return self.db.fetch_one(query, (student_id,))

    def delete_student(self, student_id):
        """Удаление студента."""
        query = "DELETE FROM students WHERE id = ?"
        self.db.execute_query(query, (student_id,))


class CourseRepository:
    """Репозиторий для работы с курсами."""

    def __init__(self, db: Database):
        self.db = db

    def add_course(self, title, credits=3):
        """Добавление нового курса."""
        query = "INSERT INTO courses (title, credits) VALUES (?, ?)"
        return self.db.execute_query(query, (title, credits))

    def get_all_courses(self):
        """Получение списка всех курсов."""
        query = "SELECT * FROM courses ORDER BY title"
        return self.db.fetch_all(query)

    def get_course_by_id(self, course_id):
        """Получение курса по ID."""
        query = "SELECT * FROM courses WHERE id = ?"
        return self.db.fetch_one(query, (course_id,))


class GradeRepository:
    """Репозиторий для работы с оценками и отчётами."""

    def __init__(self, db: Database):
        self.db = db

    def add_grade(self, student_id, course_id, grade):
        """Добавление оценки."""
        query = """
            INSERT INTO grades (student_id, course_id, grade)
            VALUES (?, ?, ?)
        """
        return self.db.execute_query(query, (student_id, course_id, grade))

    def get_student_grades(self, student_id):
        """Получить все оценки студента с названиями курсов."""
        query = """
            SELECT c.title, g.grade, g.date_received
            FROM grades g
            JOIN courses c ON g.course_id = c.id
            WHERE g.student_id = ?
            ORDER BY g.date_received DESC
        """
        return self.db.fetch_all(query, (student_id,))

    def get_average_grade_for_student(self, student_id):
        """Средний балл студента."""
        query = "SELECT AVG(grade) as avg_grade FROM grades WHERE student_id = ?"
        result = self.db.fetch_one(query, (student_id,))
        return result["avg_grade"] if result and result["avg_grade"] else 0

    def get_top_students(self, limit=3):
        """Топ N студентов по среднему баллу."""
        query = """
            SELECT s.id, s.first_name, s.last_name, AVG(g.grade) as avg_grade
            FROM students s
            JOIN grades g ON s.id = g.student_id
            GROUP BY s.id
            ORDER BY avg_grade DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (limit,))