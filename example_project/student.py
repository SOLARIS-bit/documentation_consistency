class Student:
    """
    Represents a student.

    Attributes:
        name (str): Student's name.
        age (int): Student's age.
    """

    def __init__(self, name, age):
        """
        Initialize a new student.

        Args:
            name (str): Student's name.
            age (int): Student's age.
        """
        self.name = name
        self.age = age
    def greet(self):
        """
        Greet the student.

        Returns:
            str: A greeting message.
        """
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    def is_adult(self):
        """
        Check if the student is an adult.

        Returns:
            bool: True if the student is 18 or older, False otherwise.
        """
        return self.age >= 18
    def celebrate_birthday(self):
        """
        Celebrate the student's birthday by increasing their age by 1.

        Returns:
            None
        """
        self.age += 1
    def study(self, subject):
        """
        Study a subject.

        Args:
            subject (str): The subject to study.

        Returns:
            str: A message indicating the student is studying the subject.
        """
        return f"{self.name} is studying {subject}."