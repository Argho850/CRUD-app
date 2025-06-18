from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '1122303'

# MySQL configuration
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="student_db"
        )
        return conn
    except Error as e:
        # Don't flash here, just return None
        print(f"Database connection failed: {e}")
        return None

# Dashboard route
@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
        except Error as e:
            flash(f"Database error: {e}", "danger")
            students = []
        finally:
            cursor.close()
            conn.close()
        return render_template('index.html', students=students)
    flash("Database connection failed!", "danger")
    return render_template('index.html', students=[])

# Add student route
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()

        if not name or not email:
            flash("Name and email are required!", "danger")
            return render_template('add_student.html')

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)",
                    (name, email, phone)
                )
                conn.commit()
                flash("Student added successfully!", "success")
            except Error as e:
                flash(f"Error: {e}", "danger")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('index'))
        else:
            flash("Database connection failed!", "danger")
    return render_template('add_student.html')

# Edit student route
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed!", "danger")
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()

        if not name or not email:
            flash("Name and email are required!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('edit_student', id=id))

        try:
            cursor.execute(
                "UPDATE students SET name=%s, email=%s, phone=%s WHERE id=%s",
                (name, email, phone, id)
            )
            conn.commit()
            flash("Student updated successfully!", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if student:
        return render_template('edit_student.html', student=student)
    flash("Student not found!", "danger")
    return redirect(url_for('index'))

# Delete student route
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=%s", (id,))
            conn.commit()
            flash("Student deleted successfully!", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Database connection failed!", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)