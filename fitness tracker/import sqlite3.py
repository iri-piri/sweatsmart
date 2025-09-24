import sqlite3
import os
import datetime

def create_database():
    # Create database file if it doesn't exist
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Create exercise categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercise_categories (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Create exercises table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER,
        description TEXT,
        FOREIGN KEY (category_id) REFERENCES exercise_categories (id)
    )
    ''')

    # Create workout routines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workout_routines (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        date_created TEXT NOT NULL
    )
    ''')

    # Create routine exercises junction table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS routine_exercises (
        routine_id INTEGER,
        exercise_id INTEGER,
        sets INTEGER,
        reps INTEGER,
        PRIMARY KEY (routine_id, exercise_id),
        FOREIGN KEY (routine_id) REFERENCES workout_routines (id),
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    ''')

    # Create goals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        target_value INTEGER,
        current_value INTEGER DEFAULT 0,
        category_id INTEGER,
        deadline TEXT,
        FOREIGN KEY (category_id) REFERENCES exercise_categories (id)
    )
    ''')

    # Create workout logs table to track progress
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY,
        exercise_id INTEGER,
        date TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully!")

# Call function to create database
create_database()

# Implement core function
def add_exercise_category():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    category_name = input("Enter new exercise category name: ")

    try:
        cursor.execute("INSERT INTO exercise_categories (name) VALUES (?)", (category_name,))
        conn.commit()
        print(f"Category '{category_name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"Category '{category_name}' already exists!")

    conn.close()

def view_exercises_by_category():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all categories
    cursor.execute("SELECT id, name FROM exercise_categories")
    categories = cursor.fetchall()

    if not categories:
        print("No categories found. Please add some categories first.")
        conn.close()
        return

    print("\nAvailable Categories:")
    for id, name in categories:
        print(f"{id}. {name}")

    try:
        category_id = int(input("\nEnter category ID to view exercises: "))

        # Check if category exists
        cursor.execute("SELECT name FROM exercise_categories WHERE id=?", (category_id,))
        category = cursor.fetchone()

        if not category:
            print("Category not found!")
            conn.close()
            return

        # Get exercises for selected category
        cursor.execute('''
        SELECT e.id, e.name, e.description
        FROM exercises e
        WHERE e.category_id=?
        ''', (category_id,))

        exercises = cursor.fetchall()

        if exercises:
            print(f"\nExercises in category '{category[0]}':")
            for id, name, description in exercises:
                print(f"ID: {id}, Name: {name}")
                if description:
                    print(f"Description: {description}")
                print("-----")
        else:
            print(f"No exercises found in category '{category[0]}'.")

            # Option to add exercises
            add_option = input("Would you like to add exercises to this category? (y/n): ")
            if add_option.lower() == 'y':
                add_exercise(category_id)

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def add_exercise(category_id=None):
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    if category_id is None:
        # Get all categories
        cursor.execute("SELECT id, name FROM exercise_categories")
        categories = cursor.fetchall()

        if not categories:
            print("No categories found. Please add some categories first.")
            conn.close()
            return

        print("\nAvailable Categories:")
        for id, name in categories:
            print(f"{id}. {name}")

        try:
            category_id = int(input("\nEnter category ID for the new exercise: "))

            # Check if category exists
            cursor.execute("SELECT name FROM exercise_categories WHERE id=?", (category_id,))
            category = cursor.fetchone()

            if not category:
                print("Category not found!")
                conn.close()
                return

        except ValueError:
            print("Invalid input. Please enter a number.")
            conn.close()
            return

    exercise_name = input("Enter exercise name: ")
    exercise_description = input("Enter exercise description (optional): ")

    cursor.execute(
        "INSERT INTO exercises (name, category_id, description) VALUES (?, ?, ?)",
        (exercise_name, category_id, exercise_description)
    )

    conn.commit()
    print(f"Exercise '{exercise_name}' added successfully!")
    conn.close()

def delete_exercise_category():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all categories
    cursor.execute("SELECT id, name FROM exercise_categories")
    categories = cursor.fetchall()

    if not categories:
        print("No categories found.")
        conn.close()
        return

    print("\nAvailable Categories:")
    for id, name in categories:
        print(f"{id}. {name}")

    try:
        category_id = int(input("\nEnter category ID to delete: "))

        # Check if category exists
        cursor.execute("SELECT name FROM exercise_categories WHERE id=?", (category_id,))
        category = cursor.fetchone()

        if not category:
            print("Category not found!")
            conn.close()
            return

        # Check if there are exercises in this category
        cursor.execute("SELECT COUNT(*) FROM exercises WHERE category_id=?", (category_id,))
        exercise_count = cursor.fetchone()[0]

        if exercise_count > 0:
            confirm = input(f"Category '{category[0]}' has {exercise_count} exercises. Deleting it will also delete all exercises. Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                conn.close()
                return

            # Delete all exercises in the category
            cursor.execute("DELETE FROM exercises WHERE category_id=?", (category_id,))

        # Delete the category
        cursor.execute("DELETE FROM exercise_categories WHERE id=?", (category_id,))

        conn.commit()
        print(f"Category '{category[0]}' and all its exercises have been deleted.")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def create_workout_routine():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    routine_name = input("Enter name for the new workout routine: ")
    date_created = datetime.datetime.now().strftime("%Y-%m-%d")

    # Insert the routine
    cursor.execute(
        "INSERT INTO workout_routines (name, date_created) VALUES (?, ?)",
        (routine_name, date_created)
    )
    routine_id = cursor.lastrowid

    adding_exercises = True
    while adding_exercises:
        # Get all categories
        cursor.execute("SELECT id, name FROM exercise_categories")
        categories = cursor.fetchall()

        if not categories:
            print("No categories found. Please add some categories first.")
            break

        print("\nSelect exercises by category:")
        for id, name in categories:
            print(f"{id}. {name}")

        try:
            category_id = int(input("\nEnter category ID to view exercises: "))

            # Check if category exists
            cursor.execute("SELECT name FROM exercise_categories WHERE id=?", (category_id,))
            category = cursor.fetchone()

            if not category:
                print("Category not found!")
                continue

            # Get exercises for selected category
            cursor.execute('''
            SELECT id, name FROM exercises WHERE category_id=?
            ''', (category_id,))

            exercises = cursor.fetchall()

            if not exercises:
                print(f"No exercises found in category '{category[0]}'.")
                continue

            print(f"\nExercises in category '{category[0]}':")
            for id, name in exercises:
                print(f"{id}. {name}")

            exercise_id = int(input("\nEnter exercise ID to add to routine: "))

            # Check if exercise exists
            cursor.execute("SELECT name FROM exercises WHERE id=?", (exercise_id,))
            exercise = cursor.fetchone()

            if not exercise:
                print("Exercise not found!")
                continue

            sets = int(input("Enter number of sets: "))
            reps = int(input("Enter number of reps: "))

            # Add exercise to routine
            try:
                cursor.execute(
                    "INSERT INTO routine_exercises (routine_id, exercise_id, sets, reps) VALUES (?, ?, ?, ?)",
                    (routine_id, exercise_id, sets, reps)
                )
                print(f"Exercise '{exercise[0]}' added to routine!")
            except sqlite3.IntegrityError:
                print(f"Exercise already exists in this routine!")

            add_more = input("\nAdd more exercises to routine? (y/n): ")
            if add_more.lower() != 'y':
                adding_exercises = False

        except ValueError:
            print("Invalid input. Please enter a number.")

    conn.commit()
    print(f"\nWorkout routine '{routine_name}' created successfully!")
    conn.close()

def view_workout_routines():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all routines
    cursor.execute("SELECT id, name, date_created FROM workout_routines")
    routines = cursor.fetchall()

    if not routines:
        print("No workout routines found.")
        conn.close()
        return

    print("\nAvailable Workout Routines:")
    for id, name, date in routines:
        print(f"{id}. {name} (Created: {date})")

    try:
        routine_id = int(input("\nEnter routine ID to view details: "))

        # Check if routine exists
        cursor.execute("SELECT name FROM workout_routines WHERE id=?", (routine_id,))
        routine = cursor.fetchone()

        if not routine:
            print("Routine not found!")
            conn.close()
            return

        # Get exercises in routine
        cursor.execute('''
        SELECT e.name, re.sets, re.reps, ec.name
        FROM routine_exercises re
        JOIN exercises e ON re.exercise_id = e.id
        JOIN exercise_categories ec ON e.category_id = ec.id
        WHERE re.routine_id=?
        ''', (routine_id,))

        exercises = cursor.fetchall()

        if exercises:
            print(f"\nExercises in routine '{routine[0]}':")
            print("=" * 50)
            print(f"{'Exercise':<20} {'Category':<15} {'Sets':<5} {'Reps':<5}")
            print("-" * 50)
            for name, sets, reps, category in exercises:
                print(f"{name:<20} {category:<15} {sets:<5} {reps:<5}")
        else:
            print(f"No exercises found in routine '{routine[0]}'.")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def log_workout():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all routines
    cursor.execute("SELECT id, name FROM workout_routines")
    routines = cursor.fetchall()

    if not routines:
        print("No workout routines found. Please create a routine first.")
        conn.close()
        return

    print("\nSelect a routine to log:")
    for id, name in routines:
        print(f"{id}. {name}")

    try:
        routine_id = int(input("\nEnter routine ID: "))

        # Check if routine exists
        cursor.execute("SELECT name FROM workout_routines WHERE id=?", (routine_id,))
        routine = cursor.fetchone()

        if not routine:
            print("Routine not found!")
            conn.close()
            return

        # Get exercises in routine
        cursor.execute('''
        SELECT e.id, e.name, re.sets, re.reps
        FROM routine_exercises re
        JOIN exercises e ON re.exercise_id = e.id
        WHERE re.routine_id=?
        ''', (routine_id,))

        exercises = cursor.fetchall()

        if not exercises:
            print(f"No exercises found in routine '{routine[0]}'.")
            conn.close()
            return

        workout_date = input("Enter workout date (YYYY-MM-DD) or press Enter for today: ")
        if not workout_date:
            workout_date = datetime.datetime.now().strftime("%Y-%m-%d")

        print(f"\nLogging workout for routine '{routine[0]}' on {workout_date}:")
        for ex_id, name, default_sets, default_reps in exercises:
            print(f"\nExercise: {name}")
            print(f"Default: {default_sets} sets, {default_reps} reps")

            sets = input(f"Sets completed (press Enter for default {default_sets}): ")
            sets = int(sets) if sets else default_sets

            reps = input(f"Reps completed (press Enter for default {default_reps}): ")
            reps = int(reps) if reps else default_reps

            # Log the exercise
            cursor.execute(
                "INSERT INTO workout_logs (exercise_id, date, sets, reps) VALUES (?, ?, ?, ?)",
                (ex_id, workout_date, sets, reps)
            )

            # Update goals progress if applicable
            cursor.execute('''
            SELECT g.id, g.target_value, g.current_value
            FROM goals g
            JOIN exercises e ON e.category_id = g.category_id
            WHERE e.id = ?
            ''', (ex_id,))

            goals = cursor.fetchall()
            for goal_id, target, current in goals:
                # Assuming goal is based on total reps
                new_value = current + (sets * reps)
                cursor.execute(
                    "UPDATE goals SET current_value = ? WHERE id = ?",
                    (new_value, goal_id)
                )

        conn.commit()
        print(f"\nWorkout logged successfully!")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def view_exercise_progress():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all exercises
    cursor.execute('''
    SELECT e.id, e.name, ec.name
    FROM exercises e
    JOIN exercise_categories ec ON e.category_id = ec.id
    ''')
    exercises = cursor.fetchall()

    if not exercises:
        print("No exercises found.")
        conn.close()
        return

    print("\nSelect an exercise to view progress:")
    for id, name, category in exercises:
        print(f"{id}. {name} (Category: {category})")

    try:
        exercise_id = int(input("\nEnter exercise ID: "))

        # Check if exercise exists
        cursor.execute("SELECT name FROM exercises WHERE id=?", (exercise_id,))
        exercise = cursor.fetchone()

        if not exercise:
            print("Exercise not found!")
            conn.close()
            return

        # Get logs for the exercise
        cursor.execute('''
        SELECT date, sets, reps, (sets * reps) as total_reps
        FROM workout_logs
        WHERE exercise_id=?
        ORDER BY date DESC
        ''', (exercise_id,))

        logs = cursor.fetchall()

        if logs:
            print(f"\nProgress for exercise '{exercise[0]}':")
            print("=" * 50)
            print(f"{'Date':<12} {'Sets':<5} {'Reps':<5} {'Total':<5}")
            print("-" * 50)
            for date, sets, reps, total in logs:
                print(f"{date:<12} {sets:<5} {reps:<5} {total:<5}")

            # Calculate some stats
            cursor.execute('''
            SELECT
                MAX(sets) as max_sets,
                MAX(reps) as max_reps,
                MAX(sets * reps) as max_total,
                AVG(sets) as avg_sets,
                AVG(reps) as avg_reps,
                COUNT(*) as workout_count
            FROM workout_logs
            WHERE exercise_id=?
            ''', (exercise_id,))

            stats = cursor.fetchone()
            print("\nStats:")
            print(f"Total workouts: {stats[5]}")
            print(f"Max sets: {stats[0]}")
            print(f"Max reps: {stats[1]}")
            print(f"Max total reps: {stats[2]}")
            print(f"Average sets: {stats[3]:.1f}")
            print(f"Average reps: {stats[4]:.1f}")
        else:
            print(f"No workout logs found for exercise '{exercise[0]}'.")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def set_fitness_goals():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all categories
    cursor.execute("SELECT id, name FROM exercise_categories")
    categories = cursor.fetchall()

    if not categories:
        print("No categories found. Please add some categories first.")
        conn.close()
        return

    print("\nAvailable Categories:")
    for id, name in categories:
        print(f"{id}. {name}")

    try:
        category_id = int(input("\nEnter category ID for the goal: "))

        # Check if category exists
        cursor.execute("SELECT name FROM exercise_categories WHERE id=?", (category_id,))
        category = cursor.fetchone()

        if not category:
            print("Category not found!")
            conn.close()
            return

        goal_name = input("Enter goal name: ")
        target_value = int(input("Enter target value (e.g., total reps to achieve): "))
        deadline = input("Enter deadline (YYYY-MM-DD) or press Enter for no deadline: ")

        if not deadline:
            deadline = None

        cursor.execute(
            "INSERT INTO goals (name, target_value, current_value, category_id, deadline) VALUES (?, ?, ?, ?, ?)",
            (goal_name, target_value, 0, category_id, deadline)
        )

        conn.commit()
        print(f"Fitness goal '{goal_name}' set successfully!")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def view_fitness_goals():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get all goals
    cursor.execute('''
    SELECT g.id, g.name, g.target_value, g.current_value, ec.name, g.deadline
    FROM goals g
    JOIN exercise_categories ec ON g.category_id = ec.id
    ''')

    goals = cursor.fetchall()

    if not goals:
        print("No fitness goals found.")
        conn.close()
        return

    print("\nYour Fitness Goals:")
    print("=" * 80)
    print(f"{'ID':<4} {'Goal':<20} {'Category':<15} {'Progress':<20} {'Deadline':<12}")
    print("-" * 80)

    for id, name, target, current, category, deadline in goals:
        progress_pct = (current / target) * 100 if target > 0 else 0
        progress_bar = f"{current}/{target} ({progress_pct:.1f}%)"
        deadline_str = deadline if deadline else "None"

        print(f"{id:<4} {name:<20} {category:<15} {progress_bar:<20} {deadline_str:<12}")

    conn.close()

def main_menu():
    while True:
        print("\n" + "=" * 40)
        print("FITNESS TRACKER APP")
        print("=" * 40)
        print("1. Add exercise category")
        print("2. View exercises by category")
        print("3. Delete exercise by category")
        print("4. Create workout routine")
        print("5. View workout routines")
        print("6. Log a workout")
        print("7. View exercise progress")
        print("8. Set fitness goals")
        print("9. View progress towards fitness goals")
        print("0. Quit")

        choice = input("\nEnter your choice (0-9): ")

        if choice == '1':
            add_exercise_category()
        elif choice == '2':
            view_exercises_by_category()
        elif choice == '3':
            delete_exercise_category()
        elif choice == '4':
            create_workout_routine()
        elif choice == '5':
            view_workout_routines()
        elif choice == '6':
            log_workout()
        elif choice == '7':
            view_exercise_progress()
        elif choice == '8':
            set_fitness_goals()
        elif choice == '9':
            view_fitness_goals()
        elif choice == '0':
            print("\nThank you for using the Fitness Tracker App!")
            break
        else:
            print("Invalid choice. Please enter a number between 0 and 9.")

if __name__ == "__main__":
    main_menu()