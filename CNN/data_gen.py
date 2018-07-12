
'''
This class aims to create a list of files where we can find the data and to manage
the computer memory. It gives to a preprocessor the data when needed and generates
a batch of data. The data memory size (in MB) is given and should not be exceeded.

'''

import os
import numpy as np
import preprocessing as pp

class Data_Gen:
    
    paths_to_file = None # array of paths where we can find the data
    size_of_files = None
    memory_size = None
    data_dims = None 
    segs = None
    database = None
    preprocessor = None
    
    def __init__(self, data, config):
        self.paths_to_file = []
        self.size_of_files = []
        self.database = data
        self.memory_size =  config['batch_memsize']
        self.data_dims = config['data_dims']
        self.segs = config['segs']
        self.preprocessor = pp.Preprocessor()
        paths = config['paths']
        # First check
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):   
                    path_to_file = os.path.join(path, file)
                    if(os.path.isfile(path_to_file)):
                        size = os.path.getsize(path_to_file)/(1024*1024)
                        if(size <= self.memory_size):
                            self.paths_to_file += [path_to_file]
                            self.size_of_files += [size]
                        else:
                            print('File {} will not fit in memory. Ignored'.format(path_to_file))
                    else:
                        print('Directory \'{}\' ignored.'.format(path_to_file))
            else:
                print('Path {} does not exist. Ignored'.format(path))
    
    def next_batch(self):
        # Heuristic to know which files we will consider
        batch_mem = 0
        argsort = np.argsort(self.size_of_files)
        files_in_batch= []
        counter = 0

        for k in argsort:
            if self.size_of_files[k] + batch_mem <= self.memory_size:
                files_in_batch += [self.paths_to_file[k]]
                batch_mem += self.size_of_files[k]
                counter += 1
            else:
                break
        self.size_of_files = [s for k, s in enumerate(self.size_of_files) if k not in argsort[:counter]]
        self.paths_to_file = [s for k, s in enumerate(self.paths_to_file) if k not in argsort[:counter]]

        (features, labels) = preprocessing.create_tf_dataset(files_in_batch, \
                                                            picture_shape = self.data_dims[0:2],\
                                                            segs = self.segs)
        features = np.array(features, dtype=np.float32)
        labels = np.array(labels, dtype=np.int32)        
        return (features, labels)
            
    def get_random_batch(x, y, batch_size):
        idx = np.random.choice(len(x),
                               size=batch_size,
                               replace=False)
        x_batch = x[idx]
        y_batch = y[idx]
        return (x_batch, y_batch)
                
