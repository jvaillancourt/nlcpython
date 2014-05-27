from . import header

def subplot2(idx,nrow=None,ncol=None):
   """Create a new subplot
      TODO subplots_adjust(), or subplots()?"""

   if nrow is not None and ncol is not None:
      fig = header.plt.figure()
      panels = [fig.add_subplot(111)] # big subplot for common xlabel and ylabel
      for i in xrange(nrow*ncol):
         panels.append(fig.add_subplot(nrow,ncol,i+1))
      # hid zeroth axis
      ax = panels[0]
      ax.set_visible(False)
      #ax.spines['top'].set_color('none')
      #ax.spines['bottom'].set_color('none')
      #ax.spines['left'].set_color('none')
      #ax.spines['right'].set_color('none')
      #ax.tick_params(labelcolor='w', top='off', bottom='off', left='off',
      #   right='off')
      
      # assign to header for bookkeeping
      header._fig['panel'] = panels
      header.plt.subplots_adjust(wspace=0)
   header.plt.sca(header._fig['panel'][idx])
   
