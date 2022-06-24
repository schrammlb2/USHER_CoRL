# USHER_CoRL
Code for the CoRL submission "USHER: Unbiased Sampling for Hindsight Experience Replay"

## Dependencies:
	python >= 3.7.7
	pytorch >= 1.5.1
	numpy >= 1.21.5
	gym <= 0.21.0
		support for goal conditioned environments was deprecated after this version, and moved to gym-robotics
		gym-robotics may be an alternative, but we have not tested our setup with it
	pybullet >= 2.6.5
	mujoco >= 2.1.0
	mujoco-py >= 2.0.2.9
	mpi4py >= 3.0.3
	pygame >= 2.1.0
	attrdict
	tdqm
	

## Discrete: 
	cd discrete_usher
	python clean_q_implementation
## Continuous: 
	cd continuous_usher
	Torus: bash torus_freeze.sh
	Car with Random Noise: bash car_experiment.sh
	Red Light: bash red_light.sh
	Fetch Robot: bash fetch.sh
	Throwing experiment: bash run_throwing_experiment.sh
	Simulated Mechanum robot: bash run_sim_to_real_experiment.sh
	Analytic Mechanum robot model: bash run_analytic_omnibot.sh
