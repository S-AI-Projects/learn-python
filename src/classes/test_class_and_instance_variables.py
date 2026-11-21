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

    # Shared by all dogs.
    assert fido.kind == 'canine'
    assert buddy.kind == 'canine'

    # Unique to fido.
    assert fido.name == 'Fido'

    # Unique to buddy.
    assert buddy.name == 'Buddy'

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


def test_dog_repeatability_and_isolation():
    """Verify repeatability, input isolation, and neighboring supported input.

    Source anchors:
    - line 25: assert fido.kind == 'canine'
    - line 26: assert buddy.kind == 'canine'
    - line 29: assert fido.name == 'Fido'

    Neighboring supported input:
    - Dog('Luna') -> luna.kind == 'canine', luna.name == 'Luna'

    Dependencies:
    - Pure in-memory classes; no external I/O, network, accounts, or UI dependencies.
    """
    class IsolatedDog:
        kind = 'canine'

        def __init__(self, name):
            self.name = name
            self.tricks = []

        def add_trick(self, trick):
            self.tricks.append(trick)

    # 1. First run of the fixture
    dog1 = IsolatedDog('Fido')
    dog2 = IsolatedDog('Buddy')
    dog1.add_trick('roll over')
    dog2.add_trick('play dead')
    assert dog1.kind == 'canine'
    assert dog2.kind == 'canine'
    assert dog1.name == 'Fido'
    assert dog2.name == 'Buddy'
    assert dog1.tricks == ['roll over']
    assert dog2.tricks == ['play dead']

    # 2. Interleaved neighboring run with fresh input
    neighbor = IsolatedDog('Luna')
    neighbor.add_trick('jump')
    assert neighbor.kind == 'canine'
    assert neighbor.name == 'Luna'
    assert neighbor.tricks == ['jump']

    # 3. Second run of the fixture with fresh isolated state: earlier runs cannot alter later results
    dog1_repeat = IsolatedDog('Fido')
    dog2_repeat = IsolatedDog('Buddy')
    dog1_repeat.add_trick('roll over')
    dog2_repeat.add_trick('play dead')
    assert dog1_repeat.kind == 'canine'
    assert dog2_repeat.kind == 'canine'
    assert dog1_repeat.name == 'Fido'
    assert dog2_repeat.name == 'Buddy'
    assert dog1_repeat.tricks == ['roll over']
    assert dog2_repeat.tricks == ['play dead']
    print("Repeatability and instance isolation successfully verified across runs.")
