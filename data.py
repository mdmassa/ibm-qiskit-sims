import os
from dotenv import load_dotenv
from qiskit import transpile
from qiskit.circuit import Parameter, ParameterVector, QuantumCircuit
from qiskit.circuit.library import unitary_overlap
from qiskit.primitives import StatevectorSampler
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

load_dotenv()

IBM_TOKEN = os.getenv("IBM_TOKEN")

QiskitRuntimeService.save_account(channel="ibm_quantum_platform",
                                  token=IBM_TOKEN,
                                  overwrite=True)

def get_training_data():
    df = pd.read_csv("dataset_graph7.csv", sep=",", header=None)
    training_data = df.values[:20,:]
    i = np.argsort(training_data[:,-1])
    X_train = training_data[i][:,:-1]
    return X_train

X_train = get_training_data()
num_samples = np.shape(X_train)[0]

num_features = np.shape(X_train)[1]
num_qubits = int(num_features/2)
entangler_map = [[0,2],[3,4],[2,5],[1,4],[2,3],[4,6]]

fm = QuantumCircuit(num_qubits)
training_param = Parameter("0")
feature_params = ParameterVector("x", num_qubits*2)
fm.ry(training_param, fm.qubits)

for cz in entangler_map:
    fm.cz(cz[0], cz[1])

for i in range(num_qubits):
    fm.rz(-2*feature_params[2*i+1],i)
    fm.rx(-2*feature_params[2*i],i)

x1 = 14
x2 = 19

unitary1 = fm.assign_parameters(list(X_train[x1]) + [np.pi/2])
unitary2 = fm.assign_parameters(list(X_train[x2]) + [np.pi/2])

overlap_circ = unitary_overlap(unitary1, unitary2)
overlap_circ.measure_all()
#overlap_circ.draw(scale=0.6, style="iqp")
overlap_circ.draw('mpl')
print(overlap_circ.draw('text'))
plt.show()