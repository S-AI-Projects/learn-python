"""Class Definition Syntax.

@see: https://docs.python.org/3/tutorial/classes.html#class-objects

After defining the class attributes to a class, the class object can be created by assigning the
object to a variable. The created object would have instance attributes associated with it.
"""


def test_class_objects():
    """Class Objects.

    Class objects support two kinds of operations:
    - attribute references
    - instantiation.

    An instance without an initializer starts with an empty instance dictionary
    and its attributes can still resolve from the class.
    """

    # ATTRIBUTE REFERENCES use the standard syntax used for all attribute references in
    # Python: obj.name. Valid attribute names are all the names that were in the class’s namespace
    # when the class object was created. For class MyCounter the following references are valid
    # attribute references:

    class ComplexNumber:
        """Example of the complex numbers class"""

        real = 0
        imaginary = 0

        def get_real(self):
            """Return real part of complex number."""
            return self.real

        def get_imaginary(self):
            """Return imaginary part of complex number."""
            return self.imaginary

    print(
        'class default: expected=0, actual={!r}'.format(ComplexNumber.real)
    )
    assert ComplexNumber.real == 0

    # __doc__ is also a valid attribute, returning the docstring belonging to the class
    print(
        'class doc: expected={!r}, actual={!r}'.format(
            'Example of the complex numbers class',
            ComplexNumber.__doc__,
        )
    )
    assert ComplexNumber.__doc__ == 'Example of the complex numbers class'

    # Class attributes can also be assigned to, so you can change the value of
    # ComplexNumber.counter by assignment.
    ComplexNumber.real = 10
    print(
        'updated class real: expected=10, actual={!r}'.format(
            ComplexNumber.real
        )
    )
    assert ComplexNumber.real == 10

    # CLASS INSTANTIATION uses function notation. Just pretend that the class object is a
    # parameterless function that returns a new instance of the class. For example
    # (assuming the above class):
    # Without __init__, the instance dictionary stays empty.
    # Lookup falls back to class attributes.
    complex_number = ComplexNumber()

    expected_instance_state = {}
    inherited_attributes = (complex_number.real, complex_number.imaginary)
    expected_inherited_attributes = (10, 0)
    print(
        'empty instance: expected state={!r}, actual state={!r}; '
        'expected inherited attributes={!r}, actual={!r}'.format(
            expected_instance_state,
            complex_number.__dict__,
            expected_inherited_attributes,
            inherited_attributes,
        )
    )
    assert complex_number.__dict__ == expected_instance_state
    assert complex_number.real == 10
    assert complex_number.get_real() == 10
    assert complex_number.imaginary == 0
    assert complex_number.get_imaginary() == 0
    assert complex_number.__dict__ == {}
    assert ComplexNumber.real == 10

    # Let's change counter default value back.
    ComplexNumber.real = 10
    assert ComplexNumber.real == 10

    # The instantiation operation (“calling” a class object) creates an empty object. Many classes
    # like to create objects with instances customized to a specific initial state. Therefore a
    # class may define a special method named __init__(), like this:

    class ComplexNumberWithConstructor:
        """Example of the class with constructor"""
        def __init__(self, real_part, imaginary_part):
            self.real = real_part
            self.imaginary = imaginary_part

        def get_real(self):
            """Return real part of complex number."""
            return self.real

        def get_imaginary(self):
            """Return imaginary part of complex number."""
            return self.imaginary

    complex_number = ComplexNumberWithConstructor(3.0, -4.5)
    expected_constructor_values = (3.0, -4.5)
    actual_constructor_values = (
        complex_number.real,
        complex_number.imaginary,
    )
    print(
        'constructor input=(3.0, -4.5): expected={!r}, actual={!r}'.format(
            expected_constructor_values,
            actual_constructor_values,
        )
    )
    assert actual_constructor_values == expected_constructor_values
