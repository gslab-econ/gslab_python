#!/usr/bin/env python
from abc import ABCMeta, abstractmethod
import os
import shutil
import zipfile
import zlib

class gencat(object):
    '''
    The gencat (General Concatenation) is an abstract class that concatenates files stored in a .zip 
    file in a user-specified structure and stores the new files in a .zip file. 
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, path_in, path_temp, path_out):
        '''
        path_in: path to raw data directory where data is in any number of .zip files.
        path_temp: path to temporary workspace. Workspace is created and destroyed by main method.
        path_out: path to output directory. 
        dict_name: name of dictionary to be produced.
        '''  
        self.path_in = os.path.join(path_in, '')
        self.path_temp = os.path.join(path_temp, '')
        self.path_out = os.path.join(path_out, '')
        self.dict_name = {}
    
    def main(self):
        '''
        Run all methods in order to produce fresh output. 
        Begins by wiping the path_temp and path_out directories.
        '''
        self.cleanDir(self.path_temp)
        self.cleanDir(self.path_out)
        self.unzipFiles()
        self.makeDict()
        self.writeDict()
        self.zipFiles()
        self.cleanDir(self.path_temp, new_dir = False)
    
    def cleanDir(self, path, new_dir = True):
        '''
        Remove path and all subdirectories below.
        Recreates path directory unless new_dir is False
        '''
        if path != self.path_in:
            shutil.rmtree(path, ignore_errors = True)
            if new_dir != False:
                os.makedirs(path)
    
    def unzipFiles(self):
        '''
        Unzips files from path_in to path_temp
        '''
        infilenames = os.listdir(self.path_in)
        
        for infilename in infilenames:
            infile = os.path.join(self.path_in, infilename)
        
            if zipfile.is_zipfile(infile):
                with zipfile.ZipFile(infile, 'r') as zf:
                    zf.extractall(self.path_temp)
    
    @abstractmethod
    def makeDict(self):
        '''
        This method is subclass specific because raw data may come in any format. 
        For any directory, write code to produce a dictionary where each key is the name of a file 
        to be created and each value is a tuple that contains paths to files to be concatenated. 
        Additional methods of the subclass can be defined to help construct the dictionary.
        '''
        raise Exception('Please write methods for the subclass that produce a dictionary where ' + 
                        'the keys are intended filenames and the values are a tuple of files ' + 
                        'to be concatenated to the key.') 
    
    def writeDict(self):
        '''
        Write the dictionary to output as a |-delimited text file. The elements of each tuple are
        shortened to their filenames for writing only.
        '''
        outfile_path = os.path.join(self.path_out, 'zipdict.txt')
        with open(outfile_path, 'wb') as outfile:
            
            for key in self.dict_name.keys():
                outfile.write(key)
                
                for val in self.dict_name[key]:
                    write = os.path.relpath(val, self.path_temp)
                    outfile.write('|' + write)
                
                outfile.write('\n')
    
    @abstractmethod
    def getZipSubgroups(self):
        '''
        This method should return a dictionary where each key is a distinct zipfile and the 
        values for the key are all concatenated files to be contained in the zipfile.
        '''

    def zipFiles(self):
        '''
        Concatenates all files in a dictionary values to a new file named for the corresponding key.
        Files are concatenated in the order in which they appear in the dictionary value. 
        Places NEWFILE\nFILENAME: <original filename> before each new file in the concatenation.
        Stores all concatenated files to a .zip file with ZIP64 compression in path_out.
        '''
        subgroups = self.getZipSubgroups()
        for z in subgroups.keys():
            catdirpath = os.path.join(self.path_temp, z, '')
            os.makedirs(catdirpath)
            inzippath = os.path.join('..', z, '')
            self.cleanDir(inzippath)

            outzipname = z + '.zip'
            outzippath = os.path.join(self.path_out, outzipname)
            zf         = zipfile.ZipFile(outzippath, 'a', zipfile.ZIP_DEFLATED, True)
            
            for key in subgroups[z]:
                catfilename = key + '.txt'
                catfilepath = os.path.join(catdirpath, catfilename)
                with open(catfilepath, 'ab') as catfile: 
                    for val in self.dict_name[key]:
                        catfile.write('\nNEWFILE\nFILENAME: %s\n\n' % (os.path.basename(val)))
                        with open(val, 'rU') as f:
                            for line in f:
                                catfile.write(line)
                
                inzipfile = os.path.join(inzippath, catfilename) 
                shutil.copyfile(catfilepath, inzipfile)
                zf.write(inzipfile)
        
            self.cleanDir(inzippath, new_dir = False)
