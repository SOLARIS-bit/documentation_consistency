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