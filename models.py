import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
# from sklearn.metrics import accuracy_score
# import math


class LVQ:
  def __init__(self,dtest,maxepoch,learnRate,lr_reducer):
    self.dtest = [dtest]
    self.dtrain = pd.read_csv('static/assets/datasets/datatrain.csv')
    self.dbobot = pd.read_csv('static/assets/datasets/bobot.csv')
    self.maxepoch = maxepoch
    self.learnRate = learnRate
    self.lr_reducer = lr_reducer
    self.dtrain_norm = ''
    self.dbobot_norm = ''
    self.dtest_norm = ''
    self.kelas = None
  
  def normalize(self):
    concatData=np.concatenate((self.dtrain.values,self.dbobot.values,self.dtest),axis=0)
    concatData=concatData.astype(np.float64)
    norm = MinMaxScaler()
    norm.fit(concatData[0:,0:-1])
    concatData[0:,0:-1]=norm.transform(concatData[0:,0:-1])
    self.dtrain_norm=concatData[0:-4]
    self.dbobot_norm=concatData[-4:-1]
    self.dtest_norm=concatData[-1,0:-1]
  
  def train(self):
    for epoch in range(self.maxepoch):
      for data in range(len(self.dtrain_norm)):
        ar_jarak=[]
        for bobot in range(len(self.dbobot_norm)):
          ar_jarak.append(np.sqrt(np.sum(np.square(self.dtrain_norm[data,0:-1]-self.dbobot_norm[bobot,0:-1]))))
        terdekat=ar_jarak.index(min(ar_jarak))
        if int(terdekat+1)==int(self.dtrain_norm[data,-1]):
          for item in range(len(self.dbobot_norm[terdekat,0:-1])):
            self.dbobot_norm[terdekat,item]=self.dbobot_norm[terdekat,item]+self.learnRate*(self.dtrain_norm[data,item]-self.dbobot_norm[terdekat,item])
        else:
          for item in range(len(self.dbobot_norm[terdekat,0:-1])):
            self.dbobot_norm[terdekat,item]=self.dbobot_norm[terdekat,item]-self.learnRate*(self.dtrain_norm[data,item]-self.dbobot_norm[terdekat,item])
      self.learnRate=self.learnRate*self.lr_reducer
  
  def test(self):
    ar_jarak=[]
    for bobot in range(len(self.dbobot_norm)):
      ar_jarak.append(np.sqrt(np.sum(np.square(self.dtest_norm-self.dbobot_norm[bobot,0:-1]))))
    self.kelas=ar_jarak.index(min(ar_jarak))+1
  
  def getKelas(self):
    return self.kelas
