"""This module implements the VariableUnitaryGate."""
from __future__ import annotations

from typing import Sequence

import numpy as np
import scipy as sp

from bqskit.ir.gate import Gate
from bqskit.qis.unitary.differentiable import DifferentiableUnitary
from bqskit.qis.unitary.optimizable import LocallyOptimizableUnitary
from bqskit.qis.unitary.unitarymatrix import UnitaryMatrix
from bqskit.utils.typing import is_valid_radixes


class VariableUnitaryGate(
    Gate, DifferentiableUnitary,
    LocallyOptimizableUnitary,
):
    """A Variable n-qudit unitary operator."""

    def __init__(self, num_qudits: int, radixes: Sequence[int] = []) -> None:
        """
        Creates an VariableUnitaryGate, defaulting to a qubit gate.

        Args:
            num_qudits (int) The number of qudits this gate acts on.

            radixes (Sequence[int]): The number of orthogonal
                states for each qudit. Defaults to qubits.
        """
        if num_qudits <= 0:
            raise ValueError('Expected positive integer, got %d' % num_qudits)

        if len(radixes) == 0:
            radixes = [2] * num_qudits

        if not is_valid_radixes(radixes, num_qudits):
            raise TypeError('Invalid radixes.')

        self._num_qudits = num_qudits
        self._radixes = tuple(radixes)
        self._dim = int(np.prod(self.radixes))
        self.shape = (self.dim, self.dim)
        self._num_params = 2 * self.dim**2
        self._name = 'VariableUnitaryGate(%d)' % self.num_qudits

    def get_unitary(self, params: Sequence[float] = []) -> UnitaryMatrix:
        """
        Returns the unitary for this gate, see Unitary for more info.

        Note:
            Ideally, params form a unitary matrix when reshaped,
            however, params are unconstrained so we return the closest
            UnitaryMatrix to the given matrix.
        """
        self.check_parameters(params)
        mid = len(params) // 2
        real = np.array(params[:mid], dtype=np.complex128)
        imag = 1j * np.array(params[mid:], dtype=np.complex128)
        x = real + imag
        return UnitaryMatrix.closest_to(np.reshape(x, self.shape))

    def get_grad(self, params: Sequence[float] = []) -> np.ndarray:
        """Returns the gradient for this gate, see Gate for more info."""
        raise NotImplementedError(
            'Gradient-based optimization not implemented for '
            'VariableUnitaryGate.',
        )

    def optimize(self, env_matrix: np.ndarray) -> list[float]:
        """Returns optimal parameters with respect to an environment matrix."""
        self.check_env_matrix(env_matrix)
        U, _, Vh = sp.linalg.svd(env_matrix)
        x = np.reshape(Vh.conj().T @ U.conj().T, (self.num_params // 2,))
        return list(np.real(x)) + list(np.imag(x))
