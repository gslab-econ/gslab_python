#!/usr/bin/env python
from abc import ABCMeta, abstractmethod
import os
import shutil
import zipfile

class gencat(object):
    '''
    The gencat (General Concatenation) is an abstract class that concatenates files stored in a .zip 
    file in a user-specified structure and stores the new files in a .zip file. 
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, path_in, path_temp, path_out, dict_name, zip_name):
        '''
        path_in: path to raw data directory where data is in any number of .zip files.
        path_temp: path to temporary workspace. Workspace is created and destroyed by main method.
        path_out: path to output directory. 
        dict_name: name of dictionary to be produced.
        zip_name: name of zip file to be produced. 
        '''  
        paths = [path_in, path_temp, path_out]
        for path in paths:
            if path[-1] == '/':
                path = path
            else:
                path = path + '/'
        
        self.path_in = path_in
        self.path_temp = path_temp
        self.path_out = path_out
        self.dict_name = dict_name
        self.zip_name = zip_name
        
        map_dict = dict_name + '_dict'
        self.map_dict = {}
    
    def main(self):
        '''
        Run all methods in order to produce fresh output. 
        Begins by wiping the path_temp and path_out directories.
        '''
        self.cleanDir(self.path_temp)
        self.cleanDir(self.path_out)
        self.unzipFiles()
        self.makeMapDict()
        self.writeMapDict()
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
            infile = self.path_in + infilename
        
            if zipfile.is_zipfile(infile):
                with zipfile.ZipFile(infile, 'r') as zf:
                    zf.extractall(self.path_temp)
    
    @abstractmethod
    def makeMapDict(self):
        '''
        This method is subcalss specific because raw data may come in any format. 
        For any directory, write code to produce a dictionary where each key is the name of a file 
        to be created and each value is a tuple that contains paths to files to be concatenated. 
        Additional methods of the subclass can be defined to help construct the dictionary.
        '''
        raise Exception('Please write methods for the subclass that produce a dictionary where ' + 
                        'the keys are intended filenames and the values are a tuple of files ' + 
                        'to be concatenated to the key.') 
    
    def writeMapDict(self):
        '''
        Write the dictionary to output as a |-delimited text file. The elements of each tuple are
        shortened to their filenames for writing only.
        '''
        outfile_path = self.path_out + self.dict_name + '.txt'
        with open(outfile_path, 'wb') as outfile:
            for key in self.map_dict.keys():
                outfile.write(key)
                for val in self.map_dict[key]:
                    write = val.rsplit('/')[-1]
                    outfile.write('|' + write)
                outfile.write('\n')
    
    def zipFiles(self):
        '''
        Concatenates all files in a dictionary values to a new file named for the corresponding key.
        Places NEWFILE\nFILENAME: <original filename> before each new file in the concatenation.
        Stores all concatenated files to a .zip file in path_out.
        '''
        inzippath = self.path_temp + self.zip_name + '/'
        os.makedirs(inzippath)
        
        for key in self.map_dict.keys():
            
            CATFILE = inzippath + key + '.txt'
            with open(CATFILE, 'ab') as catfile: 
                
                for val in self.map_dict[key]:
                    catfile.write('\nNEWFILE\nFILENAME: %s\n\n' % (val.rsplit('/')[-1]))
                    
                    with open(val, 'rU') as f:
                        for line in f:
                            catfile.write(line)
        
        outzippath = self.path_out + self.zip_name
        shutil.make_archive(outzippath, 'zip', self.path_temp, self.zip_name)
