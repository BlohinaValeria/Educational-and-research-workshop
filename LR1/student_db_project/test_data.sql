-- Добавление студентов
INSERT INTO students (first_name, last_name, birth_date, email) VALUES
('Иван', 'Петров', '2000-05-12', 'ivan.petrov@example.com'),
('Мария', 'Сидорова', '2001-08-23', 'maria.s@example.com'),
('Алексей', 'Иванов', '1999-11-02', 'alex.ivanov@example.com');

-- Добавление курсов
INSERT INTO courses (title, credits) VALUES
('Математика', 4),
('Программирование', 5),
('Базы данных', 4);

-- Добавление оценок
INSERT INTO grades (student_id, course_id, grade) VALUES
(1, 1, 5),
(1, 2, 4),
(2, 1, 4),
(2, 3, 5),
(3, 2, 3),
(3, 3, 4);