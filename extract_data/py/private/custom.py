#! /usr/bin/env python
import csv, time, re, operator, codecs
from private.preliminaries import lineclass
import private.messages as messages

######################################################
# Custom globals
######################################################   
#Returns a variable dictionary to be passed to subsequent processes.
def Custom_globals():
    globals = { 'itemcharvals': '//gsball-b/Nielsen_Raw/RMS2006-2010/products/ITEMCHARVALS',
                'year': 2008, 
                'module': '7738', 
                'widths_char': [[1,12],[43,46]], 
                'widths': [[1,7],[8,19],[20,27],[30,32],[37,42]], 
                'columnnames': rowclass(['MOVE_TDLINK','UPC','MOVE_WK_END','MOVE_UNIT','MOVE_PRICE']),
                'sortcols':[1,0,2,3,4],
                'sorttypes':(int,int,int,int,float)}
    globals['fields'] = len(globals['widths'])
    globals['outfilename'] = 'purchases_'+str(globals['year'])+'_'+str(globals['module'])+'.csv'
                
    return(globals)
    
    
######################################################
# Custom classes
######################################################   
#define a custom class of row objects which represent a lineclass parsed into fixed-width columns
class rowclass(list):
    def __init__(self,row):
        self.row = row
    def stripzeros(self):
        count=0
        for i in self.row:
            self.row[count]=re.sub(r"^0+","",self.row[count]).strip()
            count=count+1
    def preparecsv(self):
        linetemp=''
        for i in self.row:
            linetemp=linetemp+i+","
        linetemp=linetemp[:-1]+"\n"
        return linetemp             
        
#upc-product_module crosswalk, sorted        
class charfile:
    def __init__(self,charvalinput,widths,module):
        self.charvalinput=charvalinput
        self.widths=widths
        self.module=module
        self.extractchars()
    
    def extractchars(self):
        charfile=codecs.open(self.charvalinput, 'rU', encoding="latin-1")
        upc_prod=[]
        numfields_char = len(self.widths)
        for line in charfile:
            line = lineclass(line)
            rowtemp=rowclass(line.fixedwidth(self.widths,numfields_char))
            if rowtemp.row[1] == self.module:
                upc_prod.append(rowtemp.row)
        upc_prod.sort()
        self.proddict=dict(upc_prod)
        charfile.close()     


######################################################
# Custom functions
######################################################   
#sort final csv file according to inputted column ordering (cols)
def sortcsv(file, types, cols):
    data=[]
    colnames=[]
    count=0
    
    def converttype(types, values):
        return [t(v) for t, v in zip(types, values)]

    with open(file, 'rU') as csvfile:
        for row in csv.reader(csvfile):
            if count == 0:
                colnames = row
            if count >0:
                data.append(converttype(types,row))
            count = count + 1
    data.sort(key=operator.itemgetter(*cols))
    with open(file, 'wb') as csvfile:
        csv.writer(csvfile).writerow(colnames)
        csv.writer(csvfile).writerows(data)

def open_file(outfolder, outfilename, names):
    csvfile=open(outfolder+outfilename, 'wb')
    csvfile.write(names.preparecsv())
    
    return(csvfile)
    
def extract_characteristics(module, itemcharvals, widths_char, LOGFILE):
    defstart=time.clock()
    chars=charfile(itemcharvals,widths_char,module)
    defend=time.clock()
    print >> LOGFILE, messages.time_charfiletime % str("%.2f" % (defend - defstart))    
    
    return(chars)
    
    
######################################################
# Custom main tools
######################################################    
#Opens output file(s) and executes any other actions required by data extraction task prior to
#line-by-line extraction.
def Custom_prelims(globals, outfolder, LOGFILE):
    chars=extract_characteristics(globals['module'], globals['itemcharvals'],
        globals['widths_char'], LOGFILE)
    csvfile=open_file(outfolder, globals['outfilename'], globals['columnnames'])
    
    return({'csvfile': csvfile, 'chars': chars})

#Taking a line of raw data, this function defines the extraction process and writes output to the
#output file.     
def Custom_proc(line,globals,prelims,options,LOGFILE):
    csvfile = prelims['csvfile']
    charfile = prelims['chars']
    rowtemp=[]
    numfields = len(globals['widths'])
    
    line = lineclass(line)
    rowtemp=rowclass(line.fixedwidth(globals['widths'],numfields))
    if rowtemp.row[1] in charfile.proddict:
        rowtemp.stripzeros()
        #remove if blank MOVE_TDLINK or MOVE_WK_END
        if rowtemp.row[0].strip() and rowtemp.row[2].strip():
            csvfile.write(rowtemp.preparecsv())

#Closes output file(s) and executes any other actions requires by data extraction task after 
#line-by-line extraction.    
def Custom_wrapup(globals,outfolder,prelims,LOGFILE):
    prelims['csvfile'].close()
    
    sorttimestart = time.clock()
    sortcsv(outfolder+globals['outfilename'],globals['sorttypes'],globals['sortcols'])
    sorttimeend = time.clock()
    print >> LOGFILE, messages.time_csvsorttime % str("%.2f" % (sorttimeend - sorttimestart)) 
    
    print >> LOGFILE, messages.note_written % (outfolder+globals['outfilename'])
        