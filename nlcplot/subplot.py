from . import header

def subplot(nrow,ncol,idx,wspace=None):
   """Create a new subplot
      TODO subplots_adjust(), or subplots()?"""

   header.plt.subplot(nrow,ncol,idx)
   if wspace is not None:
      header.plt.subplots_adjust(wspace=wspace)
