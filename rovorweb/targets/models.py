from django.db import models

from fields import RAField, DecField
from redrovor.coords import Coords

from tempfile import NamedTemporaryFile

# Create your models here.


class Target(models.Model):
    '''model for target objects (i.e. astronomical objects we are observing)'''

    name = models.CharField(unique=True,max_length=100) #name we use for object
    simbadName = models.CharField(unique=True,max_length=100)  #the primary name for it in simbad
    ra = RAField()
    dec = DecField()


    def get_coords(self):
        return Coords(ra=self.ra,dec=self.dec)
    def set_coords(self, coords):
        '''set coordinates from a Coords object
        or tuple of ra and dec'''
        if not coords:
            self.ra = None
            self.dec = None
        else:
            self.ra, self.dec = coords

    coords = property(get_coords,set_coords)

    def __str__(self):
        return self.name

    def tempCoordFile(self):
        '''create a temporary file containing a coordinate list
        of the coordinates for the target, from the FieldObject
        database.
        
        This returns the path to the temporary file, and it is up to
        the user to take care of deleting it.'''
        #TODO figure out how we should order the objects
        #sort by isTarget descending so targets are at top of list
        objs = FieldObject.objects.filter(target=self).order_by('-isTarget','id')
        with NamedTemporaryFile('w',suffix='.coo',delete=False) as coofile:
            fname = coofile.name #save the name so we can return it
            for coord in objs:
                coofile.write("{0}  {1}\n".format(coord.ra.toDegrees(),coord.dec.toDegrees()))
        return fname


            



def getUploadPath(self, filename):
    '''compute the file path for an uploaded coordfile
    This assumes that the target field has been set'''
    return "coordfiles/{0:s}/{1:s}".format(self.target.name,filename)

class CoordFileModel(models.Model):
    '''model for coordinate files that have been uploaded'''
    target = models.ForeignKey(Target)  #the target the coordfile is for
    coordfile = models.FileField(upload_to=getUploadPath,null=True)


class FieldObject(models.Model):
    '''model for other objects in the field
    of a target, such as comparison stars, and the target itself'''

    target = models.ForeignKey(Target)  #the target field this coordinate is associated with
    ra = RAField()
    dec = DecField()
    isTarget = models.BooleanField()

    def get_coords(self):
        return Coords(ra=self.ra,dec=self.dec)
    def set_coords(self,coords):
        if not coords:
            self.ra = None
            self.dec = None
        else:
            self.ra,self.dec = coords
    coords = property(get_coords,set_coords)


class CalibrationMagnitudes(models.Model):
    '''model to keep track of calibration magnitudes and errors
    for each filter for each calibration star'''
    star = models.ForeignKey(FieldObject)
    filt = models.CharField(max_length=50)
    #should we use decimal fields or float fields?
    mag = models.DecimalField(decimal_places=3,max_digits=6)
    err = models.DecimalField(decimal_places=5,max_digits=7)