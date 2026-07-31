# This module contains the following functions :
#
# transport
#
# Author : Virginie Guemas - 2026
##########################################################################
import xarray as xr
import numpy as np
import sys
#
##########################################################################
def transport(u,v,s,e1u,e2u,e1v,e2v,e3u,e3v,lat,lon,umask,vmask,xward,yward):

    """ Computes the mass and freshwater transports through a section 
      provided by umask/vmask. The section can be curved up to a certain
      point : for each section point, the local orientation of the section is
      computed using the two closest points on the section and the transport
      is taken positive along x (y) if xward (yward) = True

      INPUTS:
        u = current along the x-axis (t, z, y, x) or (z, y, x)
        v = current along the y-axis (t, z, y, x) or (z, y, x)
        s = salinity                 (t, z, y, x) or (z, y, x)
        e1u = grid cell x-length on the u-grid (y, x)
        e2u = grid cell y-length on the u-grid (y, x)
        e1v = grid cell x-length on the v-grid (y, x)
        e2v = grid cell y-length on the v-grid (y, x)
        e3u = grid cell height on the u-grid (z, y, x)
        e3v = grid cell height on the v-grid (z, y, x)
        lat = latitude at t-grid (y, x)
        lon = longitude on the t-grid (y, x)
        umask = 1 on the section, 0 elsewhere on u-grid (z, y, x)
        vmask = 1 on the section, 0 elsewhere on v-grid (z, y, x)
        xward = True/False positive transport toward increasing x  
        yward = True/False positive transport toward increasing y

      OUTPUTS:
        volume     = water volume transport in Sv
        mass       = mass transport in kg/s
        freshwater = freshwater transport in Sv 

      HISTORY:
         Creation in 2026 by Virginie Guemas (CNRS/CNRM)
         
    """
    # ==========================================================================
    # Grid dimensions
    # ==========================================================================

    # Dimensions
    dims = u.shape
    if len(dims) == 4:
      (lt, lz, ly, lx) = dims
    elif len(dims) == 3:
      (lz, ly, lx) = dims
      lt = 1
    else:
      sys.exit('Dimensions for u must be (t, z, y, x) or (z, y, x)') 
    
    # TO BE DONE : Add dimension checks for all inputs
    Sref = 35. 
    #
    # TO BE DONE : Remove folded points
    #
    # ==========================================================================
    # Reduce input arrays to the section
    # ==========================================================================
    #
    # Dimensions z, y, x to z, y*x and then find y*x section point indices
    umask2d = umask.to_numpy().reshape((lz, ly*lx))
    vmask2d = vmask.to_numpy().reshape((lz, ly*lx))
    uind = np.where(umask2d[0,] > 0.5)
    vind = np.where(vmask2d[0,] > 0.5)
    umask2dmask = umask2d[:, np.union1d(uind,vind)]
    vmask2dmask = vmask2d[:, np.union1d(uind,vind)]
    
    e3u2d = umask.to_numpy().reshape((lz, ly*lx))
    e3v2d = vmask.to_numpy().reshape((lz, ly*lx))
    e3u2dmask = e3u2d[:, np.union1d(uind,vind)]
    e3v2dmask = e3v2d[:, np.union1d(uind,vind)]
    
    # Dimensions y,x to y*x and then select section points
    lon1d = lon.to_numpy().reshape((ly*lx,))
    lat1d = lat.to_numpy().reshape((ly*lx,))
    lon1dmask = lon1d[np.union1d(uind,vind)]
    lat1dmask = lat1d[np.union1d(uind,vind)]
    
    e1u1d = e1u.to_numpy().reshape((ly*lx,))
    e1v1d = e1v.to_numpy().reshape((ly*lx,))
    e2u1d = e2u.to_numpy().reshape((ly*lx,))
    e2v1d = e2v.to_numpy().reshape((ly*lx,))
    e1u1dmask = e1u1d[np.union1d(uind,vind)]
    e1v1dmask = e1v1d[np.union1d(uind,vind)]
    e2u1dmask = e2u1d[np.union1d(uind,vind)]
    e2v1dmask = e2v1d[np.union1d(uind,vind)]
    
    # Dimensions t, z, y, x to z, y*x and then select section points
    u3d = u.to_numpy().reshape((lt, lz, ly*lx))
    v3d = v.to_numpy().reshape((lt, lz, ly*lx))
    s3d = s.to_numpy().reshape((lt, lz, ly*lx))
    u3dmask = u3d[:,:, np.union1d(uind,vind)]
    v3dmask = v3d[:,:, np.union1d(uind,vind)]
    s3dmask = s3d[:,:, np.union1d(uind,vind)]
    
    # Empty outputs
    volume_transport     = np.zeros(lt)
    freshwater_transport = np.zeros(lt)
    transports = xr.Dataset()
    # ==========================================================================
    # Section geometry
    # ==========================================================================
    #
    jt = 0
    jz = 0
    for jpt in np.arange(lon1dmask.size):
      dlon = lon1dmask - lon1dmask[jpt]
      dlat = lat1dmask - lat1dmask[jpt]
    
      a = np.sin(dlat/2)**2 + np.cos(lat1dmask) * np.cos(lat1dmask[jpt]) * np.sin(dlon/2)**2
      c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
      
      closest = np.argsort(c)
      # This array contains the indices of points on the section organized starting from jpt until the farthest on the section from jpt
      
      # For each point on the section, we select the two closest ones to compute the local direction of the section : O is jpt, 1 & 2 are the closest points
      dx = lon1dmask[closest[1]]-lon1dmask[closest[2]]
      dy = lat1dmask[closest[1]]-lat1dmask[closest[2]]
      
      # Find section extremities
      if (np.abs(dx) < np.abs(lon1dmask[closest[0]]-lon1dmask[closest[2]])) or (np.abs(dx) < np.abs(lon1dmask[closest[0]]-lon1dmask[closest[1]])) or (np.abs(dy) < np.abs(lat1dmask[closest[0]]-lat1dmask[closest[2]])) or (np.abs(dy) < np.abs(lat1dmask[closest[0]]-lat1dmask[closest[1]])):
        print('End point of the section:', lon1dmask[jpt], lat1dmask[jpt])
    
        dx = lon1dmask[closest[1]]-lon1dmask[closest[0]]
        dy = lat1dmask[closest[1]]-lat1dmask[closest[0]]
    
    # ==========================================================================
    # Current locally perpendicular to the section
    # ==========================================================================
    #
      nx = np.abs( dy / np.sqrt(dx**2 + dy**2))
      ny = np.abs( dx / np.sqrt(dx**2 + dy**2))
    
      if not xward: 
        nx = -nx
    
      if not yward: 
        ny = -ny
    
      unorm = v3dmask[jt, jz, jpt] * nx
      vnorm = u3dmask[jt, jz, jpt] * ny
    
    # ==========================================================================
    # Water volume transport  
    # ==========================================================================
      
      volume_transport[jt] = volume_transport[jt] + unorm * e2u1dmask [jpt] * e3u2dmask[jz, jpt] * umask2dmask[jz, jpt]
        
      volume_transport[jt] = volume_transport[jt] + vnorm * e1v1dmask [jpt] * e3v2dmask[jz, jpt] * vmask2dmask[jz, jpt]
    
      volume_transport[jt] = volume_transport[jt] / 1e6
    
    # ==========================================================================
    # Freshwater transport 
    # ==========================================================================
      
      freshwater_transport[jt] = freshwater_transport[jt] + unorm * ((Sref - s3dmask[jt, jz, jpt] )/Sref) * e2u1dmask [jpt] * e3u2dmask[jz, jpt] * umask2dmask[jz, jpt]
    
    
      freshwater_transport[jt] = freshwater_transport[jt] + vnorm * ((Sref - s3dmask[jt, jz, jpt] )/Sref) * e1v1dmask [jpt] * e3v2dmask[jz, jpt] * vmask2dmask[jz, jpt]
    
      freshwater_transport[jt] = freshwater_transport[jt] / 1e6
    
    # ==========================================================================
    # Outputs
    # ==========================================================================
    
    transports['volume_transport'] = xr.DataArray(volume_transport, dims = ('time'), attrs = {'long_name':'Water volume transport', 'units':'Sv'}) 
    transports['freshwater_transport'] = xr.DataArray(freshwater_transport, dims = ('time'), attrs = {'long_name':'Freshwater transport', 'units':'Sv'}) 
    
    return transports
