

from TrainData import TrainData_fullTruth
from TrainData import TrainData,fileTimeOut

class TrainData_deepFlavour_FT(TrainData_fullTruth):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TrainData_fullTruth.__init__(self)
        
        
        self.addBranches(['jet_pt', 'jet_eta','nCpfcand','nNpfcand','nsv','npv'])
       
        self.addBranches(['Cpfcan_BtagPf_trackEtaRel',
                          'Cpfcan_BtagPf_trackPtRel',
                          'Cpfcan_BtagPf_trackPPar',
                          'Cpfcan_BtagPf_trackDeltaR',
                          #'Cpfcan_BtagPf_trackPtRatio',
                          'Cpfcan_BtagPf_trackPParRatio',
                          'Cpfcan_BtagPf_trackSip2dVal',
                          'Cpfcan_BtagPf_trackSip2dSig',
                          'Cpfcan_BtagPf_trackSip3dVal',
                          'Cpfcan_BtagPf_trackSip3dSig',
                          'Cpfcan_BtagPf_trackJetDistVal',
                          'Cpfcan_BtagPf_trackJetDistSig',
                          
                          'Cpfcan_ptrel', #not the same as btv ptrel!
                          #'Cpfcan_erel',
                          #'Cpfcan_phirel',
                          #'Cpfcan_etarel',
                          #'Cpfcan_pt',
                          #'Cpfcan_dxy',
                          #'Cpfcan_dxyerrinv',
                          #'Cpfcan_dz',
                          
                          'Cpfcan_drminsv',
                          'Cpfcan_fromPV',
                          'Cpfcan_VTX_ass',
                          
                          'Cpfcan_puppiw',
                          'Cpfcan_chi2',
                          'Cpfcan_quality'
                              ],
                             25)
        
        
        self.addBranches([#'Npfcan_erel',
                          'Npfcan_ptrel',
                          'Npfcan_deltaR',
                          #'Npfcan_phirel',
                          #'Npfcan_etarel',
                              'Npfcan_isGamma',
                              'Npfcan_HadFrac',
                              'Npfcan_drminsv',
                              
                              'Npfcan_puppiw'
                              ],
                             25)
        
        
        self.addBranches(['sv_pt',
                              #'sv_etarel',
                              #'sv_phirel',
                              'sv_deltaR',
                              'sv_mass',
                              'sv_ntracks',
                              'sv_chi2',
                              #'sv_ndf',
                              'sv_normchi2',
                              'sv_dxy',
                              #'sv_dxyerr',
                              'sv_dxysig',
                              'sv_d3d',
                              #'sv_d3derr',
                              'sv_d3dsig',
                              'sv_costhetasvpv',
                              'sv_enratio',
                              ],
                             4)

        
        
       
    def readFromRootFile(self,filename,TupleMeanStd, weighter):
        from preprocessing import MeanNormApply, MeanNormZeroPad, MeanNormZeroPadParticles
        import numpy
        from stopwatch import stopwatch
        
        sw=stopwatch()
        swall=stopwatch()
        
        import ROOT
        
        fileTimeOut(filename,120) #give eos a minute to recover
        rfile = ROOT.TFile(filename)
        tree = rfile.Get("deepntuplizer/tree")
        self.nsamples=tree.GetEntries()
        
        print('took ', sw.getAndReset(), ' seconds for getting tree entries')
        
        
        # split for convolutional network
        
        x_global = MeanNormZeroPad(filename,TupleMeanStd,
                                   [self.branches[0]],
                                   [self.branchcutoffs[0]],self.nsamples)
        
        x_cpf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[1],
                                   self.branchcutoffs[1],self.nsamples)
        
        x_npf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[2],
                                   self.branchcutoffs[2],self.nsamples)
        
        x_sv = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[3],
                                   self.branchcutoffs[3],self.nsamples)
        
        
        
        print('took ', sw.getAndReset(), ' seconds for mean norm and zero padding (C module)')
        
        Tuple = self.readTreeFromRootToTuple(filename)
        
        if self.remove:
            notremoves=weighter.createNotRemoveIndices(Tuple)
            undef=Tuple['isUndefined']
            notremoves-=undef
            print('took ', sw.getAndReset(), ' to create remove indices')
        
        if self.weight:
            weights=weighter.getJetWeights(Tuple)
        elif self.remove:
            weights=notremoves
        else:
            print('neither remove nor weight')
            weights=numpy.empty(self.nsamples)
            weights.fill(1.)
        
        
        truthtuple =  Tuple[self.truthclasses]
        #print(self.truthclasses)
        alltruth=self.reduceTruth(truthtuple)
        
        #print(alltruth.shape)
        if self.remove:
            print('remove')
            weights=weights[notremoves > 0]
            x_global=x_global[notremoves > 0]
            x_cpf=x_cpf[notremoves > 0]
            x_npf=x_npf[notremoves > 0]
            x_sv=x_sv[notremoves > 0]
            alltruth=alltruth[notremoves > 0]
       
        newnsamp=x_global.shape[0]
        print('reduced content to ', int(float(newnsamp)/float(self.nsamples)*100),'%')
        self.nsamples = newnsamp
        
        print(x_global.shape,self.nsamples)

        self.w=[weights]
        self.x=[x_global,x_cpf,x_npf,x_sv]
        self.y=[alltruth]
        



class TrainData_deepFlavour_FT_map(TrainData_deepFlavour_FT):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TrainData_deepFlavour_FT.__init__(self)
        
        self.registerBranches(['Cpfcan_ptrel','Cpfcan_eta','Cpfcan_phi',
                               'Npfcan_ptrel','Npfcan_eta','Npfcan_phi',
                               'nCpfcand','nNpfcand',
                               'jet_eta','jet_phi','jet_pt'])
        

        
        
       
    def readFromRootFile(self,filename,TupleMeanStd, weighter):
        from preprocessing import MeanNormApply, MeanNormZeroPad, createDensityMap, MeanNormZeroPadParticles
        import numpy
        from stopwatch import stopwatch
        
        sw=stopwatch()
        swall=stopwatch()
        
        import ROOT
        
        fileTimeOut(filename,120) #give eos a minute to recover
        rfile = ROOT.TFile(filename)
        tree = rfile.Get("deepntuplizer/tree")
        self.nsamples=tree.GetEntries()
        
        print('took ', sw.getAndReset(), ' seconds for getting tree entries')
        
        
        # split for convolutional network
        
        x_global = MeanNormZeroPad(filename,TupleMeanStd,
                                   [self.branches[0]],
                                   [self.branchcutoffs[0]],self.nsamples)
        
        x_cpf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[1],
                                   self.branchcutoffs[1],self.nsamples)
        
        x_npf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[2],
                                   self.branchcutoffs[2],self.nsamples)
        
        x_sv = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[3],
                                   self.branchcutoffs[3],self.nsamples)
        
        
        #here the difference starts
        x_chmap = createDensityMap(filename,TupleMeanStd,
                                   'Cpfcan_ptrel',
                                   self.nsamples,
                                   ['Cpfcan_eta','jet_eta',20,0.5],
                                   ['Cpfcan_phi','jet_phi',20,0.5],
                                   'nCpfcand',-1)
        
        x_neumap = createDensityMap(filename,TupleMeanStd,
                                   'Npfcan_ptrel',
                                   self.nsamples,
                                   ['Npfcan_eta','jet_eta',20,0.5],
                                   ['Npfcan_phi','jet_phi',20,0.5],
                                   'nNpfcand',-1)
        
        
        print('took ', sw.getAndReset(), ' seconds for mean norm and zero padding (C module)')
        
        Tuple = self.readTreeFromRootToTuple(filename)
        
        if self.remove:
            notremoves=weighter.createNotRemoveIndices(Tuple)
            undef=Tuple['isUndefined']
            notremoves-=undef
            print('took ', sw.getAndReset(), ' to create remove indices')
        
        if self.weight:
            weights=weighter.getJetWeights(Tuple)
        elif self.remove:
            weights=notremoves
        else:
            print('neither remove nor weight')
            weights=numpy.empty(self.nsamples)
            weights.fill(1.)
        
        
        truthtuple =  Tuple[self.truthclasses]
        #print(self.truthclasses)
        alltruth=self.reduceTruth(truthtuple)
        
        #print(alltruth.shape)
        if self.remove:
            print('remove')
            weights=weights[notremoves > 0]
            x_global=x_global[notremoves > 0]
            x_cpf=x_cpf[notremoves > 0]
            x_npf=x_npf[notremoves > 0]
            x_sv=x_sv[notremoves > 0]
            
            x_chmap=x_chmap[notremoves > 0]
            x_neumap=x_neumap[notremoves > 0]
            
            alltruth=alltruth[notremoves > 0]
       
        newnsamp=x_global.shape[0]
        print('reduced content to ', int(float(newnsamp)/float(self.nsamples)*100),'%')
        self.nsamples = newnsamp
        
        print(x_global.shape,self.nsamples)

        self.w=[weights]
        self.x=[x_global,x_cpf,x_npf,x_sv,x_chmap,x_neumap]
        self.y=[alltruth]
        
class TrainData_image(TrainData_fullTruth):
    '''
    This class is for simple jetimiging
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(TrainData_image,self).__init__()

        self.addBranches(['jet_pt', 'jet_eta','nCpfcand','nNpfcand','nsv','npv'])

        self.registerBranches(['Cpfcan_ptrel','Cpfcan_eta','Cpfcan_phi',
                               'Npfcan_ptrel','Npfcan_eta','Npfcan_phi',
                               'nCpfcand','nNpfcand',
                               'jet_eta','jet_phi','jet_pt'])

        self.regtruth='gen_pt_WithNu'
        self.regreco='jet_corr_pt'
        
        self.registerBranches([self.regtruth,self.regreco])
       
    def readFromRootFile(self,filename,TupleMeanStd, weighter):
        from preprocessing import MeanNormApply, MeanNormZeroPad, createDensityMap, CreateCountMap, MeanNormZeroPadParticles 
        import numpy
        from stopwatch import stopwatch
        
        sw=stopwatch()
        swall=stopwatch()
        
        import ROOT
        
        fileTimeOut(filename,120) #give eos a minute to recover
        rfile = ROOT.TFile(filename)
        tree = rfile.Get("deepntuplizer/tree")
        self.nsamples=tree.GetEntries()
        
        print('took ', sw.getAndReset(), ' seconds for getting tree entries')
        
        # split for convolutional network
        
        x_global = MeanNormZeroPad(filename,TupleMeanStd,
                                   [self.branches[0]],
                                   [self.branchcutoffs[0]],self.nsamples)    
        
        #here the difference starts
        x_chmap = createDensityMap(filename,TupleMeanStd,
                                   'Cpfcan_ptrel',
                                   self.nsamples,
                                   ['Cpfcan_eta','jet_eta',20,0.5],
                                   ['Cpfcan_phi','jet_phi',20,0.5],
                                   'nCpfcand',-1)
        
        x_chcount = createCountMap(filename,TupleMeanStd,
                                   self.nsamples,
                                   ['Cpfcan_eta','jet_eta',20,0.5],
                                   ['Cpfcan_phi','jet_phi',20,0.5],
                                   'nCpfcand')
        
        x_neumap = createDensityMap(filename,TupleMeanStd,
                                   'Npfcan_ptrel',
                                   self.nsamples,
                                   ['Npfcan_eta','jet_eta',20,0.5],
                                   ['Npfcan_phi','jet_phi',20,0.5],
                                   'nNpfcand',-1)
        
        x_neucount = createCountMap(filename,TupleMeanStd,
                                   self.nsamples,
                                   ['Npfcan_eta','jet_eta',20,0.5],
                                   ['Npfcan_phi','jet_phi',20,0.5],
                                   'nNpfcand')
        
        
        print('took ', sw.getAndReset(), ' seconds for mean norm and zero padding (C module)')
        
        Tuple = self.readTreeFromRootToTuple(filename)
        
        if self.remove:
            notremoves=weighter.createNotRemoveIndices(Tuple)
            undef=Tuple['isUndefined']
            notremoves-=undef
            print('took ', sw.getAndReset(), ' to create remove indices')
        
        if self.weight:
            weights=weighter.getJetWeights(Tuple)
        elif self.remove:
            weights=notremoves
        else:
            print('neither remove nor weight')
            weights=numpy.ones(self.nsamples)

        pttruth=Tuple[self.regtruth]
        ptreco=Tuple[self.regreco]         
        
        truthtuple =  Tuple[self.truthclasses]
        #print(self.truthclasses)
        alltruth=self.reduceTruth(truthtuple)
        
        x_map = numpy.concatenate((x_chmap,x_chcount,x_neumap,x_neucount), axis=3)
        
        #print(alltruth.shape)
        if self.remove:
            print('remove')
            weights=weights[notremoves > 0]
            x_global=x_global[notremoves > 0]
            x_map=x_map[notremoves > 0]
            alltruth=alltruth[notremoves > 0]
            pttruth=pttruth[notremoves > 0]
            ptreco=ptreco[notremoves > 0]
        newnsamp=x_global.shape[0]
        print('reduced content to ', int(float(newnsamp)/float(self.nsamples)*100),'%')
        self.nsamples = newnsamp
        print(x_global.shape,self.nsamples)

        self.w=[weights]
        self.x=[x_global,x_map, ptreco]
        self.y=[alltruth,pttruth]
       
    @staticmethod
    def base_model(input_shapes):
        from keras.layers import Input
        from keras.layers.core import Masking
        x_global  = Input(shape=input_shapes[0])
        x_map = Input(shape=input_shapes[1])
        x_ptreco  = Input(shape=input_shapes[2])

        x =   Convolution2D(64, (8,8)  , border_mode='same', activation='relu',kernel_initializer='lecun_uniform')(Inputs[1])
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x =   Convolution2D(64, (4,4) , border_mode='same', activation='relu',kernel_initializer='lecun_uniform')(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x =   Convolution2D(64, (4,4)  , border_mode='same', activation='relu',kernel_initializer='lecun_uniform')(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x = Flatten()(x)
        x = merge( [x, Inputs[1]] , mode='concat')
        # linear activation for regression and softmax for classification
        x = Dense(128, activation='relu',kernel_initializer='lecun_uniform')(x)

        return [x_global, x_map, x_ptreco], x

    @staticmethod
    def regression_generator(generator):
        for X, Y in generator:
            yield X, Y[1]#.astype(int)

    @staticmethod
    def regression_model(input_shapes):
        inputs, x = TrainData_image.base_model(input_shapes)
        predictions = Dense(2, activation='linear',init='normal')(x)
        return Model(inputs=inputs, outputs=predictions)

    @staticmethod
    def classification_generator(generator):
        for X, Y in generator:
            yield X, Y[0]#.astype(int)

    @staticmethod
    def classification_model(input_shapes, nclasses):
        inputs, x = TrainData_image.base_model(input_shapes)
        predictions = Dense(nclasses, activation='softmax',kernel_initializer='lecun_uniform')(x)
        return Model(inputs=inputs, outputs=predictions)

    @staticmethod
    def model(input_shapes, nclasses):
        inputs, x = TrainData_image.base_model(input_shapes)
        predictions = [
            Dense(nclasses, activation='softmax',kernel_initializer='lecun_uniform')(x),
            Dense(2, activation='linear',init='normal')(x)
        ]
        return Model(inputs=inputs, outputs=predictions)
