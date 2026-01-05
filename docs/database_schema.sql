-- AbsenceBot database schema

CREATE TABLE students (
    id VARCHAR(32) PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    major VARCHAR(100) NOT NULL,
    UNIQUE KEY uq_student_name_grade_major (full_name, grade, major)
);

CREATE TABLE absences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    teacher_id INT NOT NULL,
    absence_date DATE NOT NULL,
    created_at DATETIME NOT NULL,
    UNIQUE KEY uq_absence_student_day (student_id, absence_date)
);
