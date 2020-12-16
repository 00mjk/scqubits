from typing import Any, Dict, Tuple

import numpy as np
from numpy import ndarray

import scqubits.core.descriptors as descriptors
import scqubits.io_utils.fileio_serializers as serializers
import scqubits.core.qubit_base as base
from scqubits import VariationalTightBinding


# -Transmon using VariationalTightBinding

class TransmonVTB(VariationalTightBinding, base.QubitBaseClass, serializers.Serializable):
    EJ = descriptors.WatchedProperty('QUANTUMSYSTEM_UPDATE', attr_name='EJlist', attr_location=1)
    EC = descriptors.WatchedProperty('QUANTUMSYSTEM_UPDATE')
    ng = descriptors.WatchedProperty('QUANTUMSYSTEM_UPDATE', attr_name='nglist', attr_location=1)
    num_exc = descriptors.WatchedProperty('QUANTUMSYSTEM_UPDATE')

    def __init__(self,
                 EJ: float,
                 EC: float,
                 ng: float,
                 truncated_dim: int = None,
                 **kwargs
                 ) -> None:
        VariationalTightBinding.__init__(self, np.array([EJ]), np.array([ng]), 0.0,
                                         number_degrees_freedom=1, number_periodic_degrees_freedom=1, **kwargs)
        self.EJ = EJ
        self.EC = EC
        self.ng = ng
        self.truncated_dim = truncated_dim
        self._sys_type = type(self).__name__

    @staticmethod
    def default_params() -> Dict[str, Any]:
        return {
            'EJ': 15.0,
            'EC': 0.3,
            'ng': 0.0,
            'truncated_dim': 10
        }

    def build_gamma_matrix(self, minimum: int = 0) -> ndarray:
        gamma_matrix = np.array([[0.0]])
        min_loc = self.sorted_minima()[minimum]
        gamma_list = self.EJlist / self.Phi0 ** 2
        gamma_matrix[0, 0] = gamma_list[0] * np.cos(min_loc[0])
        return gamma_matrix

    def _build_all_exp_i_phi_j_operators(self, Xi: ndarray, a_operator_list: ndarray) -> ndarray:
        return self._build_single_exp_i_phi_j_operator(0, Xi, a_operator_list)

    def _local_potential(self, exp_i_phi_j: ndarray, premultiplied_a_a_dagger: Tuple[ndarray, ndarray, ndarray],
                         Xi: ndarray, phi_neighbor: ndarray, minima_m: ndarray, minima_p: ndarray) -> ndarray:
        phi_bar = 0.5 * (phi_neighbor + (minima_m + minima_p))
        exp_i_phi_j = exp_i_phi_j * np.exp(1j * phi_bar[0])
        potential_matrix = -0.5 * self.EJlist[0] * (exp_i_phi_j + exp_i_phi_j.conjugate())
        potential_matrix += self.EJlist[0] * self.identity()
        return potential_matrix

    def potential(self, phi: ndarray) -> ndarray:
        return -self.EJ * np.cos(phi[0])

    def build_EC_matrix(self)-> ndarray:
        return np.array([[self.EC]])

    def build_capacitance_matrix(self) -> ndarray:
        return np.array([[self.e**2 / (2 * self.EC)]])

    def sorted_minima(self) -> ndarray:
        return np.array([[0.0]])