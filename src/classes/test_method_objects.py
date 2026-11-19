"""Class Definition Syntax.

@see: https://docs.python.org/3/tutorial/classes.html#method-objects

Classes can have two types of attribute references: data or methods. Class methods are called
by [variable_name].[method_name]([parameters]) as opposed to class data which lacks the ().
"""
import random
import sys


class MyCounter:
    """A simple example of the counter class"""
    counter = 10

    def get_counter(self):
        """Return the counter"""
        return self.counter

    def increment_counter(self):
        """Increment the counter"""
        self.counter += 1
        return self.counter


def test_method_objects():
    """Method Objects."""

    # The other kind of instance attribute reference is a method. A method is a function that
    # “belongs to” an object. (In Python, the term method is not unique to class instances: other
    # object types can have methods as well. For example, list objects have methods called append,
    # insert, remove, sort, and so on. However, in the following discussion, we’ll use the term
    # method exclusively to mean methods of class instance objects, unless explicitly stated
    # otherwise.)

    # But be aware that counter.get_counter() is not the same thing as MyCounter.get_counter() —
    # it is a method object, not a function object.

    # Usually, a method is called right after it is bound
    counter = MyCounter()
    assert counter.get_counter() == 10

    # However, it is not necessary to call a method right away: counter.get_counter() is a method
    # object, and can be stored away and called at a later time. For example:
    get_counter = counter.get_counter
    assert get_counter() == 10

    # What exactly happens when a method is called? You may have noticed that counter.get_counter()
    # was called without an argument above, even though the function definition for get_counter()
    # specified an argument (self). What happened to the argument? Surely Python raises an
    # exception when a function that requires an argument is called without any — even if the
    # argument isn’t actually used…

    # Actually, you may have guessed the answer: the special thing about methods is that the
    # instance object is passed as the first argument of the function. In our example, the call
    # counter.get_counter() is exactly equivalent to MyCounter.get_counter(counter). In general,
    # calling a method with a list of n arguments is equivalent to calling the corresponding
    # function with an argument list that is created by inserting the method’s instance object
    # before the first argument.

    assert counter.get_counter() == 10
    assert MyCounter.get_counter(counter) == 10

    # Neighboring supported input derived independently:
    # Increment counter by 1 to reach neighboring state 11
    assert counter.increment_counter() == 11
    assert counter.get_counter() == 11
    assert get_counter() == 11
    assert MyCounter.get_counter(counter) == 11


def test_method_objects_property():
    """Property test verifying method object binding and mutation invariant.

    Invariant contract:
      For any MyCounter instance with counter value C:
        obj.get_counter() == (obj.get_counter)() == MyCounter.get_counter(obj) == C
      Invoking (obj.increment_counter)() increments counter to C + 1, and subsequent
      evaluations of bound get_counter() evaluate to C + 1.
      Repeated runs with fresh equivalent instances yield identical results.

    Source anchors:
      assert counter.get_counter() == 10
      assert get_counter() == 10
      assert counter.get_counter() == 10

    Neighboring supported input:
      counter.increment_counter() == 11
      counter.get_counter() == 11
    """
    # Small readable case
    c = MyCounter()
    c.counter = 0
    assert c.get_counter() == 0
    bound_get = c.get_counter
    bound_inc = c.increment_counter
    assert bound_get() == 0
    assert bound_inc() == 1
    assert bound_get() == 1
    assert MyCounter.get_counter(c) == 1

    # Property test over 100 bounded valid cases with fixed seed
    rng = random.Random(42)
    for _ in range(100):
        init_val = rng.randint(-1000, 1000)
        num_increments = rng.randint(0, 20)

        inst = MyCounter()
        inst.counter = init_val
        m_get = inst.get_counter
        m_inc = inst.increment_counter

        # Invariant before increments
        assert inst.get_counter() == init_val
        assert m_get() == init_val
        assert MyCounter.get_counter(inst) == init_val

        # Apply increments
        for step in range(1, num_increments + 1):
            res = m_inc()
            assert res == init_val + step

        # Invariant after increments
        expected_final = init_val + num_increments
        assert inst.get_counter() == expected_final
        assert m_get() == expected_final
        assert MyCounter.get_counter(inst) == expected_final


def test_method_objects_regression():
    """Focused regression test for test_method_objects contract.

    Verifies:
      - Return value of test_method_objects() is None.
      - Zero observable mutation on module attributes or global state.
    """
    current_module = sys.modules[__name__]
    attrs_before = set(dir(current_module))

    ret = test_method_objects()
    assert ret is None

    attrs_after = set(dir(current_module))
    assert attrs_before == attrs_after
