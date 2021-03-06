# This is part of MiMiCPy

"""

This module contains the MDP class that
allows for pythonic creation/manipulation of
Gromacs MDP script

"""

from mimicpy.scripts.mdp import Mdp
from ..utils.errors import ParserError

class MDP(Mdp):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
        if 'title' in kwargs:
            self.name = kwargs['title']
        
        if not self.hasparam('name'):
            self.name = 'MD Run'
    
    def edit(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
            
    @classmethod
    def defaultEM(cls):
        return cls(name = 'Minim',
                   integrator = "steep",  # Algorithm (steep = steepest descent minimization)
                   emtol = 1000.0, # Stop minimization when the maximum force < 1000.0 kJ/mol/nm
                   emstep = 0.01,  # Minimization step size
                   nstlog = 50,
                   nsteps = 50000, # Maximum number of (minimization) steps to perform
                   nstlist = 10, # Frequency to update the neighbor list and long range forces
                   cutoff_scheme = "Verlet", # Buffered neighbor searching 
                   ns_type = "grid", # Method to determine neighbor list (simple, grid)
                   coulombtype = "PME", #Treatment of long range electrostatic interactions
                   rcoulomb = 1.0,# Short-range electrostatic cut-off
                   rvdw = 1.0, # Short-range Van der Waals cut-off
                   pbc = 'xyz'
                   )
        
    @classmethod
    def defaultNVT(cls):
        return cls(name = 'NVT', 
                   define = '-DPOSRES',  # position restrain the protein/ligands
                   # Run parameters
                   integrator = 'md', #leap-frog integrator
                   nsteps = 50000, # 2 * 50000 = 100 ps
                   dt = 0.002, #2 fs
                   # Output control
                   nstxout = 500, # save coordinates every 1.0 ps
                   nstvout = 500, # save velocities every 1.0 ps
                   nstenergy = 500, # save energies every 1.0 ps
                   nstlog = 500, # update log file every 1.0 ps
                   #Bond parameters
                   continuation = 'no', # first dynamics run
                   constraint_algorithm = 'lincs', # holonomic constraints 
                   constraints = 'h_bonds', # bonds involving H are constrained
                   lincs_iter = 1, # accuracy of LINCS
                   lincs_order = 4, # also related to accuracy
                   # Nonbonded settings 
                   cutoff_scheme = 'Verlet', # Buffered neighbor searching
                   ns_type = 'grid', # search neighboring grid cells
                   nstlist = 10, # largely irrelevant with Verlet
                   rcoulomb = 1.0, # short-range electrostatic cutoff (in nm)
                   rvdw = 1.0, # short-range van der Waals cutoff (in nm)
                   DispCorr = 'EnerPres', # account for cut-off vdW scheme
                   # Electrostatics
                   coulombtype = 'PME', # Particle Mesh Ewald for long-range electrostatics
                   pme_order   = 4, # cubic interpolation
                   fourierspacing = 0.16, # grid spacing for FFT
                   # Temperature coupling is on
                   tcoupl = 'V-rescale', # modified Berendsen thermostat
                   tc_grps = 'Protein Non-Protein', # two coupling groups - more accurate
                   tau_t = '0.1     0.1', # time constant, in ps
                   ref_t = '300     300', # reference temperature, one for each group, in K
                   # Pressure coupling is off
                   pcoupl = 'no', # no pressure coupling in NVT
                   # Periodic boundary conditions
                   pbc    = 'xyz', # 3-D PBC
                   # Velocity generation
                   gen_vel = 'yes', # assign velocities from Maxwell distribution
                   gen_temp = 300, # temperature for Maxwell distribution
                   gen_seed = -1, # generate a random seed
                   )
    @classmethod   
    def defaultNPT(cls):
        npt = cls.defaultNVT()
        npt.name = 'NPT'
        npt.continuation = 'yes'
        npt.pcoupl = 'Parrinello-Rahman' # Pressure coupling on in NPT
        npt.pcoupltype = 'isotropic' # uniform scaling of box vectors
        npt.tau_p = 2.0 # time constant, in ps
        npt.ref_p = 1.0  # reference pressure, in bar
        npt.compressibility = '4.5e-5' # isothermal compressibility of water in 1/bar
        npt.refcoord_scaling = 'com'
        npt.DispCorr = 'EnerPres' # account for cut-off vdW scheme
        npt.pbc = 'xyz' # 3D PBC
        # Velocity generation
        npt.gen_vel = 'no' # Velocity generation is off 
        npt.gen_vel = None
        npt.gen_temp = None
        npt.gen_seed = None
        
        return npt
     
    @classmethod
    def defaultMD(cls):
        eq = cls.defaultNPT()
        eq.name = 'MD'
        eq.define = None
        eq.nstxout = 10000
        eq.nstvout = 0
        eq.nstfout = 0
        eq.nstenergy = 5000
        eq.nstlog  = 5000
        eq.refcoord_scaling = None

        return eq
    
    @classmethod
    def defaultMiMiC(cls):
        return cls(integrator = 'mimic', # will be set by prepare.QM.getInp() anyways
                   nsteps = 100000,
                   dt = 0.0001, # around 4 hartree
                   # Output control
                   nstxout = 10000, # save coordinates every 100 steps
                   nstvout = 10000, # save velocities every 100 steps
                   nstfout = 10000, # save forces every 100 stesp
                   nstenergy = 0, # energies not necessary as they are not accurate in MiMiC run (use CPMD output)
                   nstlog = 5000, # update log file every 50 steps
                   # Bond parameters
                   continuation = 'no', # first dynamics run
                   constraints = 'none', # no constraints as we want QM region to be flexible
                   # Neighbor searching
                   cutoff_scheme = 'Verlet',
                   ns_type = 'grid', # search neighboring grid cells
                   nstlist = 10,
                   rcoulomb = 1.0, # short-range electrostatic cutoff (in nm)
                   rvdw = 1.0, # short-range van der Waals cutoff (in nm)
                   # Electrostatics
                   coulombtype = 'PME', # Particle Mesh Ewald for long-range electrostatics
                   pme_order = 4, # cubic interpolation
                   fourierspacing = 0.16, # grid spacing for FFT
                   # Temperature coupling is off - no need for that as CPMD will be the integrator
                   tcoupl = 'no',
                   pcoupl = 'no',
                   # Periodic boundary conditions
                   pbc = 'xyz', # 3-D PBC
                   # Dispersion correction
                   DispCorr = 'EnerPres', # account for cut-off vdW scheme
                   # Velocity generation
                   gen_vel = 'no' # do not generate velocities
                   # QMMM-grps = QMatoms will be set by prepare.QM.getInp()
                   )
