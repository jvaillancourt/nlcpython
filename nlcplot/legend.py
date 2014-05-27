from . import header

def legend(numpoints=1,loc='best',**args):
   """Place a legend on the figure
   
      Supported optional arguments:
      size - font size
   """

   a = header.translateArgs(**args)

   header.plt.legend(numpoints=numpoints,loc=loc,fontsize=a['fontsize'])
