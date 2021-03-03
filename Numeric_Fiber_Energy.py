import numpy as np
import System as Sys
import Shape as Sh
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from InfiniteFilamentsTriangles_v1 import *

import InfiniteFilamentsTriangles_v1 as T
import InfiniteFilamentsHexagons_v1 as H

def line(x,a,b):
    return a*x+b
class BF:
    def __init__(self,WidthMax,P,type=1):
        #Make an array of system for each W
        self.Wmax = WidthMax
        self.Aspect = np.array([1./3.,1./5.,0.1])
        self.type=type
        #self.Aspect = np.array([1./10.,1./50.,0.01])
        if P.ParticleType == 'Triangle':
            self.width_list, self.energy_list, BulkE = \
                    T.DetermineInfiniFilamentEnergy(P.k, P.k, P.kc, \
                                                    P.kA, P.kA, \
                                                    1., \
                                                    P.epsilon, 0., WidthMax)
        elif P.ParticleType == 'Hexagon':
            self.width_list,self.energy_list1, self.energy_list2, BulkE = \
                    H.DetermineInfiniFilamentEnergy(P.k, P.k, P.kc, \
                                                    P.kA, P.kA, \
                                                    1., \
                                                    P.epsilon, 0., WidthMax)
        self.Systems = np.array([np.empty(3,dtype=object) for w in range(0,WidthMax,1)])
    def Np(self,W,L,P):
        if P.ParticleType=='Hexagon':
            if W ==1:
                return L
            else :
                return (W)*L # Careful if the type of fiber
        else :
            return W*L
    def CheckInfFiber(self,w,P):
        E=list()
        if w >= self.Wmax:
            w = self.Wmax
        if not self.Systems[w-1][0]:
            for n,a in enumerate(self.Aspect):
                self.Systems[w-1][n] = Sys.System(
                Sh.Fiber(w,int(w/a),ParticleType=P.ParticleType,type = self.type),
                Kmain=P.k,
                eps=P.epsilon,
                Kcoupling=P.kc,
                Kvol=P.kA,
                ParticleType=P.ParticleType)
        for i,S in enumerate(self.Systems[w-1]):
            A = self.Aspect[i]
            #S.PrintPerSite('k'+str(P.k)+'_kA'+str(P.kA)+'_kc'+str(P.kc)+'_A'+str(A)+'.res')
            #loop over several aspect ratio
            FiberArray = Sh.Fiber(w,int(w/A),ParticleType=P.ParticleType,type=self.type)
            SurfaceEnergy = Sh.SurfaceEnergy(FiberArray,J=P.J,ParticleType=P.ParticleType)
            E.append((S.Energy+SurfaceEnergy)/self.Np(w,int(w/A),P))#(w*int(w/A)))

        popt,pconv = curve_fit(line,self.Aspect,E)
        #np.savetxt('Energy.txt',E)
        print('a, b = '+str(popt))
        fig,ax = plt.subplots()
        ax.plot(self.Aspect,line(self.Aspect,popt[0],popt[1]))
        ax.scatter(self.Aspect,E)
        return fig, ax
    def Get_E(self,w,P,type=0):
        if P.ParticleType == 'Triangle':
            return self.energy_list[w-1]+P.J/w
        elif P.ParticleType == 'Hexagon':
            if type == 1:
                return self.energy_list1[w-1]+4*P.J/w
            elif type ==2:
                return self.energy_list2[w-1]+4*P.J/w
            else :
                print('fiber type not precised')
                return 0.
    def Get_Einf(self,w,P):
        E=list()
        if w >= self.Wmax:
            w = self.Wmax
        if not self.Systems[w-1][0]:
            for n,a in enumerate(self.Aspect):
                self.Systems[w-1][n] = Sys.System(
                Sh.Fiber(w,int(w/a),ParticleType=P.ParticleType,type=self.type),
                Kmain=P.k,
                eps=P.epsilon,
                Kcoupling=P.kc,
                Kvol=P.kA,
                ParticleType=P.ParticleType)
        for i,S in enumerate(self.Systems[w-1]):
            A = self.Aspect[i]
            #loop over several aspect ratio
            FiberArray = Sh.Fiber(w,int(w/A),ParticleType=P.ParticleType,type=self.type)
            SurfaceEnergy = Sh.SurfaceEnergy(FiberArray,J=P.J,ParticleType=P.ParticleType)
            E.append((S.Energy+SurfaceEnergy)/self.Np(w,int(w/A),P))#(w*int(w/A)))
        try :
            popt,pconv = curve_fit(line,self.Aspect,E)
        except ValueError:
            for s in self.Systems[w-1]:
                print(s.Energy)
            print(w)
            print(E)
            raise
        return popt[1]

    def Get_Best_Fiber(self,P,type=0):
        # given a set of parameter, return the width and the energy of the best
        # fiber for this set of parameter
        w=1
        if P.ParticleType=='Triangle':
            Einf1 = self.Get_E(w,P)
        else:
            Einf1 = self.Get_E(w,P,type)
        w+=1
        if P.ParticleType=='Triangle':
            Einf2 = self.Get_E(w,P)
        else :
            Einf2 = self.Get_E(w,P,type)
        while Einf2<Einf1 :
            w+=1
            Einf1=Einf2
            if P.ParticleType=='Triangle':
                Einf2 = self.Get_E(w,P)
            else :
                Einf2 = self.Get_E(w,P,type)
            if w>=self.Wmax-1:
                return w,Einf2
            #while we haven't found the best fiber
        return w-1,Einf1
