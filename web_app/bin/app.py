import web
from subprocess import call
import shlex as sh
from numpy import loadtxt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from materials_model.DPAF import *
from materials_model.VMLH import *
from materials_model.VMAF import *
from materials_model.DPLH import *
# from VMLH import *
urls = (
  '/DPAF', 'DPAF',
  '/VMLH', 'VMLH',
  '/VMAF', 'VMAF',
  '/DPLH', 'DPLH'
)

app = web.application(urls, globals())




if __name__ == "__main__":
    app.run()