from . import header

def colorbar(orient='vertical'):
   """Plot a colorbar on the image.
   
      orient - can be either vertical or horizontal"""

   header.plt.colorbar(orientation=orient,pad=0.01)
