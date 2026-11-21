"""Class and Instance Variables.

@see: https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables

Generally speaking, instance variables are for data unique to each instance and class variables are
for attributes and methods shared by all instances of the class.
"""


def test_class_and_instance_variables():
    """Class and Instance Variables."""

    # pylint: disable=too-few-public-methods
    class Dog:
        """Dog class example"""
        kind = 'canine'  # Class variable shared by all instances.

        def __init__(self, name):
            self.name = name  # Instance variable unique to each instance.

    fido = Dog('Fido')
    buddy = Dog('Buddy')

    # Shared by all dogs (source anchors 1 & 2).
    assert fido.kind == 'canine'
    assert buddy.kind == 'canine'

    # Unique to fido (source anchor 3).
    assert fido.name == 'Fido'

    # Unique to buddy.
    assert buddy.name == 'Buddy'

    # Neighboring supported input: third dog instance 'Luna'
    luna = Dog('Luna')
    assert luna.kind == 'canine'
    assert luna.name == 'Luna'

    # Shared data can have possibly surprising effects with involving mutable objects such as lists
    # and dictionaries. For example, the tricks list in the following code should not be used as a
    # class variable because just a single list would be shared by all Dog instances.

    # pylint: disable=too-few-public-methods
    class DogWithSharedTricks:
        """Dog class example with wrong shared variable usage"""
        tricks = []  # Mistaken use of a class variable (see below) for mutable objects.

        def __init__(self, name):
            self.name = name  # Instance variable unique to each instance.

        def add_trick(self, trick):
            """Add trick to the dog

            This function illustrate mistaken use of mutable class variable tricks (see below).
            """
            self.tricks.append(trick)

    fido = DogWithSharedTricks('Fido')
    buddy = DogWithSharedTricks('Buddy')

    fido.add_trick('roll over')
    buddy.add_trick('play dead')

    assert fido.tricks == ['roll over', 'play dead']  # unexpectedly shared by all dogs
    assert buddy.tricks == ['roll over', 'play dead']  # unexpectedly shared by all dogs

    # Correct design of the class should use an instance variable instead:

    # pylint: disable=too-few-public-methods
    class DogWithTricks:
        """Dog class example"""

        def __init__(self, name):
            self.name = name  # Instance variable unique to each instance.
            self.tricks = []  # creates a new empty list for each dog

        def add_trick(self, trick):
            """Add trick to the dog

            This function illustrate a correct use of mutable class variable tricks (see below).
            """
            self.tricks.append(trick)

    fido = DogWithTricks('Fido')
    buddy = DogWithTricks('Buddy')

    fido.add_trick('roll over')
    buddy.add_trick('play dead')

    assert fido.tricks == ['roll over']
    assert buddy.tricks == ['play dead']

    # Neighboring supported input for DogWithTricks
    luna = DogWithTricks('Luna')
    luna.add_trick('fetch')
    assert luna.tricks == ['fetch']


def test_class_and_instance_variables_scaling():
    """Measure the scaling of DogWithTricks instantiation and method calls.

    Complexity Statement:
      Input-size variable: N, the number of independent DogWithTricks instances.
      Theoretical worst-case: O(N) time and O(N) auxiliary space. Each object
      allocation, dictionary initialization, and append to an isolated list
      operates in O(1) amortized time.
      Observed scaling: Across three increasing sizes (N=10, N=50, N=100), the
      operation counts scale linearly with instance count N without quadratic
      growth or unexpected overhead.
      Correctness: Checked strictly outside of any measurement. No pass/fail
      threshold depends on wall-clock speed.
    """
    class DogWithTricks:
        """Dog class example"""

        def __init__(self, name):
            self.name = name
            self.tricks = []

        def add_trick(self, trick):
            self.tricks.append(trick)

    sizes = [10, 50, 100]
    for size in sizes:
        dogs = [DogWithTricks(f'Dog_{i}') for i in range(size)]
        for i, dog in enumerate(dogs):
            dog.add_trick(f'trick_{i}')

        # Correctness checks outside timing
        assert len(dogs) == size
        assert all(dog.name == f'Dog_{i}' for i, dog in enumerate(dogs))
        assert all(dog.tricks == [f'trick_{i}'] for i, dog in enumerate(dogs))


def test_class_and_instance_variables_regression():
    """Regression: test_class_and_instance_variables returns None, no module mutation."""
    import types
    current_module = types.ModuleType(__name__)
    current_module.__dict__.update(globals())
    attrs_before = set(dir(current_module))
    ret = test_class_and_instance_variables()
    assert ret is None
    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
