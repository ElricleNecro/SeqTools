import inspect
from typing import Sequence
from future.utils import raise_from
from .common import basic_getitem


class MappingException(Exception):
    pass


class Mapping(Sequence):
    def __init__(self, f, sequences, debug_msg=None):
        assert callable(f), "f must be callable"
        assert len(sequences) > 0, "at least one input sample must be provided"
        self.sequences = sequences
        self.f = f
        self.debug_msg = debug_msg

    def __len__(self):
        return len(self.sequences[0])

    @basic_getitem
    def __getitem__(self, item):
        try:
            return self.f(*(l[item] for l in self.sequences))

        except Exception as e:
            if self.debug_msg is not None:
                raise_from(e, MappingException(self.debug_msg))
            else:
                raise

    def __iter__(self):
        for args in zip(*self.sequences):
            try:
                yield self.f(*args)

            except Exception as e:
                if self.debug_msg is not None:
                    raise_from(e, MappingException(self.debug_msg))
                else:
                    raise


def smap(f, *sequence):
    """Return mapping of `f` over a sequence.

    Equivalent to :code:`[f(x) for x in sequence]` with on-demand evaluation.

    If several sequences are passed, they will be zipped together and their
    items will be passed as distinct arguments to f:
    :code:`[f(*x) for x in zip(*sequences)]`

    Example:

    >>> a = [1, 2, 3, 4]
    >>> print([v + 2 for v in a])
    [3, 4, 5, 6]
    >>> m = smap(lambda x: x + 2, a)
    >>> print([v for v in m])
    [3, 4, 5, 6]
    >>> def do(y, z):
    ...     print("computing now")
    ...     return y + z
    ...
    >>> a, b = [1, 2, 3, 4], [4, 3, 2, 1]
    >>> m = smap(do, a, b)
    >>> print([v for v in m])
    computing now
    computing now
    computing now
    computing now
    [5, 5, 5, 5]
    """
    stack = [
        (filename,
         lineno,
         function,
         code_context[0].strip('\n') if code_context else '?')
        for _, filename, lineno, function, code_context, _ in inspect.stack()
    ][1:11][::-1]
    debug_msg = "in smap created at:\n" + "\n".join(
        "  File \"{}\", line {}, in {}\n    {}".format(*st) for st in stack)

    return Mapping(f, sequence, debug_msg)


def starmap(f, sequence):
    """Similar to :func:`smap` but the elements of the sequence are assumed to
    be tuple of arguments for `f`.
    """
    return smap(lambda x: f(*x), sequence)