#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

from sympy import *
from sympy.physics.quantum import TensorProduct
from sympy.physics.quantum import tensor_product_simp
from sympy.physics.quantum import Dagger
from IPython.display import display, Math, Latex
from cmath import *
import matplotlib.pyplot as plt

from logicqubit.gates import *

class LogicQuBit:

    def __init__(self, num = 3, symbolic=False):
        self.num = num
        self.symbolic = symbolic
        self.measured_qubits = []
        self.measured_values = []
        self.operations = []
        if(not self.symbolic):
            self.phi = self.product([self.ket(0) for i in range(num)]) # o qubit 1 é o mais a esquerda
        else:
            a = symbols([str(i) + "a" + str(i) + "_0" for i in range(1, self.num + 1)])
            b = symbols([str(i) + "b" + str(i) + "_1" for i in range(1, self.num + 1)])
            self.phi = self.product([a[i]*self.ket(0)+b[i]*self.ket(1) for i in range(num)])

    def addOp(self, operation, values):
        op = str(operation)+"("+str(values[0])
        for value in values[1:]:
            op+=","+str(value)
        op += ")"
        self.operations.append(op)

    def onehot(self, i, value):
        if(i == value):
            return 1
        else:
            return 0

    def texfix(self, value):
        tex = latex(value).replace(' \cdot ', '')
        for i in range(1, self.num+1):
            tex = tex.replace(str(i) + 'a', 'a')
            tex = tex.replace(str(i) + 'b', 'b')
        return tex

    def ket(self, value, d = 2):
        return Matrix([[self.onehot(i, value)] for i in range(d)])

    def product(self, list):
        A = list[0] # atua no qubit 1 que é o mais a esquerda
        for M in list[1:]:
            A = TensorProduct(A, M)
        return A

    def getOrdListSimpleGate(self, target, Gate):
        list = []
        for i in range(1,self.num+1):
            if i == target:
                list.append(Gate)
            else:
                list.append(eye(2))
        return list

    def getOrdListCtrlGate(self, control, target, Gate):
        list1 = []
        list2 = []
        for i in range(1,self.num+1):
            if i == control:
                list1.append(Gates.P0())
                list2.append(Gates.P1())
            elif i == target:
                list1.append(eye(2))
                list2.append(Gate)
            else:
                list1.append(eye(2))
                list2.append(eye(2))
        return list1, list2

    def getOrdListCtrl2Gate(self, control1, control2, target, Gate):
        list1 = []
        list2 = []
        for i in range(1,self.num+1):
            if i == control1 or i == control2:
                list1.append(eye(2))
                list2.append(Gates.P1())
            elif i == target:
                list1.append(eye(2))
                list2.append(Gate)
            else:
                list1.append(eye(2))
                list2.append(eye(2))
        return list1, list2

    def X(self, target):
        self.addOp("X", [target])
        list = self.getOrdListSimpleGate(target, Gates.X())
        self.phi = self.product(list)*self.phi

    def Y(self, target):
        self.addOp("Y", [target])
        list = self.getOrdListSimpleGate(target, Gates.Y())
        self.phi = self.product(list)*self.phi

    def Z(self, target):
        self.addOp("Z", [target])
        list = self.getOrdListSimpleGate(target, Gates.Z())
        self.phi = self.product(list)*self.phi

    def H(self, target):
        self.addOp("H", [target])
        list = self.getOrdListSimpleGate(target, Gates.H())
        self.phi = self.product(list)*self.phi

    def U1(self, target, _lambda):
        self.addOp("U1", [target, _lambda])
        list = self.getOrdListSimpleGate(target, Gates.U1(_lambda))
        self.phi = self.product(list)*self.phi

    def CX(self, control, target):
        self.addOp("CX", [control, target])
        list1,list2 = self.getOrdListCtrlGate(control, target, Gates.X())
        product = self.product(list1) + self.product(list2)
        self.phi = product*self.phi
        return self.phi

    def CNOT(self, control, target):
        return self.CX(control, target)

    def CU1(self, control, target, _lambda):
        self.addOp("CU1", [control, target, _lambda])
        list1,list2 = self.getOrdListCtrlGate(control, target, Gates.U1(_lambda))
        product = self.product(list1) + self.product(list2)
        self.phi = product*self.phi
        return self.phi

    def CCX(self, control1, control2, target):
        self.addOp("CCX", [control1, control2, target])
        Gate = Gates.X()-eye(2)
        list1,list2 = self.getOrdListCtrl2Gate(control1, control2, target, Gate)
        product = self.product(list1) + self.product(list2)
        self.phi = product*self.phi
        return self.phi

    def Toffoli(self, control1, control2, target):
        return self.CCX(control1, control2, target)

    def DensityMatrix(self):
        density_m = self.phi*self.phi.adjoint() # |phi><phi|
        return density_m

    def Measure_One(self, target):
        self.addOp("Measure", [target])
        density_m = self.DensityMatrix()
        list = self.getOrdListSimpleGate(target, Gates.P0())
        P0 = self.product(list)
        list = self.getOrdListSimpleGate(target, Gates.P1())
        P1 = self.product(list)
        measure_0 = (density_m*P0).trace()
        measure_1 = (density_m*P1).trace()
        self.measured_qubits = target
        self.measured_values = [measure_0, measure_1]
        return [measure_0, measure_1]

    def Measure(self, target):
        self.addOp("Measure", target)
        target.sort()
        self.measured_qubits = target
        density_m = self.DensityMatrix()
        size_p = len(target)  # número de bits a ser medidos
        size = 2 ** size_p
        result = []
        for i in range(size):
            tlist = [eye(2) for tl in range(self.num)]
            blist = [i >> bl & 0x1 for bl in range(size_p)] # bits de cada i
            cnt = 0
            for j in range(self.num):
                if j + 1 == target[cnt]:
                    if blist[cnt] == 0:
                        tlist[j] = Gates.P0()
                    else:
                        tlist[j] = Gates.P1()
                    cnt += 1
                    if (cnt >= size_p):
                        break
            M = self.product(tlist)
            measure = (density_m * M).trace()
            result.append(measure)
        self.measured_values = result
        return result

    def Plot(self):
        size_p = len(self.measured_qubits)  # número de bits a ser medidos
        size = 2 ** size_p
        names = ["|" + "{0:b}".format(i).zfill(size_p) + ">" for i in range(size)]
        values = self.measured_values
        plt.bar(names, values)
        plt.suptitle('')
        plt.show()

    def Pure(self):
        density_m = self.DensityMatrix()
        pure = (density_m*density_m).trace()
        return pure

    def Print(self):
        if(not self.symbolic):
            tex = latex(self.phi)
        else:
            tex = self.texfix(self.phi)
        print(tex)

    def PrintTex(self):
        if(not self.symbolic):
            tex = latex(self.phi)
        else:
            tex = self.texfix(self.phi)
        display(Math(tex))