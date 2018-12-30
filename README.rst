install
=======
conda create -n grass python=2.7 gdal libssh2


sinks.py

	identifies sinks, classify sinks with depth > maskdepth into a sink mask for accumulation

	args
		elevation
		maskdepth = 5

	returns
		sinks
		sinkmask


hydrolines.py

	calculates hydrolines from conditioned dem and sinkmask

	args
		elevation : the conditioned anisotropically filtered dem
		sinkmask

	returns
		stream lines