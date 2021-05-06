"""This module implements the CircuitGate class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bqskit.ir.circuit import Circuit

from bqskit.ir.gate import Gate


class CircuitGate(Gate):
    """
    The CircuitGate class.

    A CircuitGate is a immutable circuit represented as a gate.
    """

    def __init__(self, circuit: Circuit, move: bool = False) -> None:
        """
        CircuitGate Constructor.

        Args:
            circuit (Circuit): The circuit to copy into gate format.

            move (bool): If true, the constructor will not copy the circuit.
                This should only be used when you are sure `circuit` will no
                longer be used on caller side. If unsure use the default.
                (Default: False)
        """

        self._circuit = circuit if move else circuit.copy()
        self.size = self._circuit.get_size()
        self.radixes = self._circuit.get_radixes()
        self.utry = self._circuit.get_unitary()

    def is_differentiable(self) -> bool:
        """Return true if the circuit is differentiable."""
        return self._circuit.is_differentiable()
