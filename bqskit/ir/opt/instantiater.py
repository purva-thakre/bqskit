"""This module implements the Instantiater base class."""
from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import numpy as np

from bqskit.qis.state.state import StateVector
from bqskit.qis.unitary.unitarymatrix import UnitaryMatrix
from bqskit.utils.typing import is_integer

if TYPE_CHECKING:
    from bqskit.ir.circuit import Circuit
    from bqskit.qis.state.state import StateLike
    from bqskit.qis.unitary.unitarymatrix import UnitaryLike


class Instantiater(abc.ABC):
    """
    The Instantiater class.

    An Instantiater is responsible for instantiating circuit templates such that
    the resulting circuit bests implements the desired target.
    """

    @abc.abstractmethod
    def instantiate(
        self,
        circuit: Circuit,
        target: UnitaryMatrix | StateVector,
        x0: np.ndarray,
    ) -> np.ndarray:
        """
        Instantiate `circuit` to best implement `target`.

        Args:
            circuit (Circuit): The circuit template to instantiate.

            target (UnitaryMatrix | StateVector): The unitary matrix to
                implement or state to prepare.

            x0 (np.ndarray): Initial point to use during instantiation.

        Returns:
            (np.ndarray): The paremeters for the circuit that makes the
                circuit best implement `target`.

        Notes:
            This method should be side-effect free. This is necessary since
            many instantiate calls to the same circuit using the same
            Instantiater object may happen in parallel.
        """

    @staticmethod
    @abc.abstractmethod
    def is_capable(circuit: Circuit) -> bool:
        """Return true if the circuit can be instantiated."""

    @staticmethod
    @abc.abstractmethod
    def get_violation_report(circuit: Circuit) -> str:
        """
        Return a message explaining why `circuit` cannot be instantiated.

        Args:
            circuit (Circuit): Generate a report for this circuit.

        Raises:
            ValueError: If `circuit` can be instantiated with this
                instantiater.
        """

    def gen_starting_points(
        self,
        multistarts: int,
        circuit: Circuit,
        target: UnitaryMatrix | StateVector,
    ) -> list[np.ndarray]:
        """
        Generate `multistarts` starting points for instantiation.

        Args:
            multistarts (int): The number of starting points to generate.

            circuit (Circuit): The circuit to generate the points for.

            target (UnitaryMatrix | StateVector): The target.

        Return:
            (list[np.ndarray]): List of starting inputs for instantiation.

        Raises:
            ValueError: If `multistarts` is not a positive integer.
        """
        if not is_integer(multistarts):
            raise TypeError(
                'Expected int for multistarts, got %s.' % type(multistarts),
            )

        if multistarts <= 0:
            raise ValueError(
                'Expected positive integer for multistarts'
                ', got %d' % multistarts,
            )

        return [  # [ circuit.get_params() ] + [  # TODO: re-evaluate
            np.random.random(circuit.num_params)
            for i in range(multistarts)
        ]

    def check_target(
        self,
        target: UnitaryLike | StateLike,
    ) -> UnitaryMatrix | StateVector:
        """Check `target` to be valid and return it casted."""
        try:
            typed_target = StateVector(target)  # type: ignore
        except (ValueError, TypeError):
            try:
                typed_target = UnitaryMatrix(target)  # type: ignore
            except (ValueError, TypeError) as ex:
                raise TypeError(
                    'Expected either StateVector, UnitaryMatrix, or'
                    ' CostFunction for target, got %s.' % type(target),
                ) from ex

        return typed_target

    @staticmethod
    @abc.abstractmethod
    def get_method_name() -> str:
        """Return the name of this method."""
