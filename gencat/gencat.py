#!/usr/bin/env python
import os
import shutil
import zipfile
import zlib
from abc import ABCMeta, abstractmethod

class gencat(object):
    '''
    Tool for concatenating text files stored in .zip files

    gencat (General Concatenation) is an abstract class that concatenates
    files stored in a .zip file in a user-specified structure and stores 
    the new files in a .zip file. Its constructor takes the following
    as argumnets:
        - path_in: the path to the directory containing the .zip files holding the
            text files that we wish to concatenate.
        - path_temp: the path to a temporary directory used in the intermediate
            stages of file concatenation. This directory is created and destroyed 
            by the class's main method.
        - path_out: the path to the directory to which a gencat object will save
            its final output. 
    '''

    __metaclass__ = ABCMeta
    
    def __init__(self, path_in, path_temp, path_out):
        self.path_in = os.path.join(path_in, '')
        self.path_temp = os.path.join(path_temp, '')
        self.path_out = os.path.join(path_out, '')
        self.concat_dict = {}
        self.zip_dict = {}

    
    def main(self):
        '''
        Run all methods in order to produce fresh output. 
        Begins by wiping the path_temp and path_out directories.
        '''
        self.cleanDir(self.path_temp)
        self.cleanDir(self.path_out)
        self.unzipFiles()
        self.makeConcatDict()
        self.makeZipDict()
        self.checkDicts()
        self.writeDict(self.concat_dict, 'concatDict.txt', self.path_temp)
        self.writeDict(self.zip_dict, 'zipDict.txt', '.')
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
    def makeConcatDict(self):
        '''
        This method should assign a dictionary to self.concat_dict where each key is a distinct concatenated  
        filename and the values for the key are all raw files to be concatenated.
        '''
        pass
    
    @abstractmethod
    def makeZipDict(self):
        '''
        This method should assign a dictionary to self.zip_dict where each key is a distinct zipfile and the 
        values for the key are all concatenated files to be contained in the zipfile.
        '''
        pass
        
    def checkDicts(self):
        '''
        Raises an exception if ZipDict or ConcatDict is empty or has non-tuple values.
        '''
        for d in [self.concat_dict, self.zip_dict]:
            if not d:
                raise Exception('THe dictionary %s must be non-empty' % (d))
            else:
                for key in d:
                    if not type(d[key]) is tuple:
                        raise TypeError('All keys in dictionary %s must be tuples. Check key %s, and try again.' % (d, key))
    
    
    def writeDict(self, dict, name, rel_path):
        '''
        Write the dictionary to output as a |-delimited text file. The elements of each tuple are
        shortened to their filenames for writing only.
        '''
        outfile_path = os.path.join(self.path_out, name)
        with open(outfile_path, 'wb') as outfile:
            
            for key in sorted(dict.keys()):
                outfile.write(key)
                
                for val in dict[key]:
                    write = os.path.relpath(val, rel_path)
                    outfile.write('|' + write)
                
                outfile.write('\n')
    
    
    def zipFiles(self):
        '''
        Concatenates all files in a dictionary values to a new file named for the corresponding key.
        Files are concatenated in the order in which they appear in the dictionary value. 
        Places NEWFILE\nFILENAME: <original filename> before each new file in the concatenation.
        Stores all concatenated files to .zip file(s) with ZIP64 compression in path_out.
        '''
        for zip_key in self.zip_dict.keys():
            catdirpath = os.path.join(self.path_temp, zip_key, '')
            os.makedirs(catdirpath)
            inzippath = os.path.join('..', zip_key, '')
            self.cleanDir(inzippath)

            outzipname = zip_key + '.zip'
            outzippath = os.path.join(self.path_out, outzipname)
            zf         = zipfile.ZipFile(outzippath, 'a', zipfile.ZIP_DEFLATED, True)
            
            for zip_val in self.zip_dict[zip_key]:
                catfilename = zip_val + '.txt'
                catfilepath = os.path.join(catdirpath, catfilename)
                with open(catfilepath, 'ab') as catfile:
                    concat_key = zip_val 
                    for concat_val in self.concat_dict[concat_key]:
                        catfile.write('\nNEWFILE\nFILENAME: %s\n\n' % (os.path.basename(concat_val)))
                        with open(concat_val, 'rU') as f:
                            for line in f:
                                catfile.write(line)
                
                inzipfile = os.path.join(inzippath, catfilename) 
                shutil.copyfile(catfilepath, inzipfile)
                zf.write(inzipfile)
        
            self.cleanDir(inzippath, new_dir = False)
