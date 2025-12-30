class Teacher:
    """
    Represents a teacher.

    Attributes:
        name (str): Teacher's name.
        subject (str): The subject they teach.
    """

    def __init__(self, name, subject):
        """
        Initialize a new teacher.

        Args:
            name (str): Name of the teacher.
            subject (str): Subject the teacher teaches.
        """
        self.name = name
        self.subject = subject
    def introduce(self):
        """
        Introduce the teacher.

        Returns:
            str: A message introducing the teacher.
        """
        return f"Hello, I am {self.name}, and I teach {self.subject}."
    def assign_homework(self, homework):
        """
        Assign homework to students.

        Args:
            homework (str): The homework assignment.

        Returns:
            str: A message about the assigned homework.
        """
        return f"{self.name} has assigned the following homework: {homework}"
    def grade_assignment(self, student_name, assignment, grade):
        """
        Grade a student's assignment.

        Args:
            student_name (str): The name of the student.
            assignment (str): The assignment being graded.
            grade (str): The grade received.

        Returns:
            str: A message about the graded assignment.
        """
        return f"{self.name} graded {student_name}'s {assignment} with a grade of {grade}."
    def hold_office_hours(self, time):
        """
        Announce office hours.

        Args:
            time (str): The time of the office hours.

        Returns:
            str: A message about the office hours.
        """
        return f"{self.name} will hold office hours at {time}."
    def provide_feedback(self, student_name, feedback):
        """
        Provide feedback to a student.

        Args:
            student_name (str): The name of the student.
            feedback (str): The feedback to provide.

        Returns:
            str: A message about the provided feedback.
        """
        return f"{self.name} provided feedback to {student_name}: {feedback}"